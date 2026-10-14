"""FastAPI app factory for the User Service (port 8001 by default)."""
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import text
from starlette.exceptions import HTTPException as StarletteHTTPException

import app.models  # noqa: F401  (registers tables)
from app.config import Settings, get_settings
from app.database import Base, make_engine, make_session_factory
from app.errors import AppError
from app.logging_config import request_id_ctx, setup_logging
from app.routes import router

REQUEST_ID_HEADER = "X-Request-ID"


def _error(status_code: int, code: str, message: str, request: Request, details=None):
    return JSONResponse(
        status_code=status_code,
        content={"error": {
            "code": code,
            "message": message,
            "details": details or [],
            "request_id": getattr(request.state, "request_id", "-"),
        }},
    )


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    logger = setup_logging(settings.service_name, settings.log_level)

    api = FastAPI(
        title="User Service",
        version="1.0.0",
        description="Owns user profiles and status (ACTIVE/INACTIVE) for the movie ticket booking system.",
    )
    engine = make_engine(settings.database_url)
    Base.metadata.create_all(engine)
    api.state.engine = engine
    api.state.session_factory = make_session_factory(engine)

    @api.middleware("http")
    async def correlation_and_logging(request: Request, call_next):
        rid = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())
        request.state.request_id = rid
        request_id_ctx.set(rid)
        start = time.perf_counter()
        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = rid
        logger.info("request completed", extra={"extra_fields": {
            "method": request.method, "path": request.url.path,
            "status": response.status_code,
            "duration_ms": round((time.perf_counter() - start) * 1000, 2)}})
        return response

    @api.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        logger.warning(f"{exc.code}: {exc.message}")
        return _error(exc.status_code, exc.code, exc.message, request, exc.details)

    @api.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError):
        details = [{"field": ".".join(str(p) for p in e["loc"][1:]) or str(e["loc"][0]),
                    "message": e["msg"]} for e in exc.errors()]
        return _error(422, "VALIDATION_ERROR", "Request validation failed", request, details)

    @api.exception_handler(StarletteHTTPException)
    async def http_handler(request: Request, exc: StarletteHTTPException):
        code = {404: "NOT_FOUND", 405: "METHOD_NOT_ALLOWED"}.get(exc.status_code, "HTTP_ERROR")
        return _error(exc.status_code, code, str(exc.detail), request)

    @api.exception_handler(Exception)
    async def unhandled(request: Request, exc: Exception):
        logger.exception("unhandled error")
        return _error(500, "INTERNAL_ERROR", "Internal server error", request)

    @api.get("/health", tags=["ops"], summary="Health check")
    def health():
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "service": settings.service_name}

    api.include_router(router)
    return api


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=get_settings().port)
