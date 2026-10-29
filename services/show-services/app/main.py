import logging
import os
import time
import uuid

from app.speed_data import seed
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import text
from starlette.exceptions import HTTPException as StarletteHTTPException

from app import models  # Register SQLAlchemy models
from app.database import (
    Base,
    get_database_url,
    make_engine,
    make_session_factory,
)
from app.routes import router


logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("show-service")

REQUEST_ID_HEADER = "X-Request-ID"


def error_response(
    status_code: int,
    code: str,
    message: str,
    request: Request,
    details=None,
):
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details or [],
                "request_id": getattr(
                    request.state, "request_id", "-"
                ),
            }
        },
    )


def create_app(database_url: str | None = None) -> FastAPI:
    api = FastAPI(
        title="Show Service",
        version="1.0.0",
        description=(
            "Manages movie shows and seat availability "
            "for the movie ticket booking system."
        ),
    )

    resolved_url = database_url or get_database_url()
    engine = make_engine(resolved_url)

    Base.metadata.create_all(bind=engine)
    seed()
    api.state.engine = engine
    api.state.session_factory = make_session_factory(engine)

    @api.middleware("http")
    async def request_logging(request: Request, call_next):
        request_id = (
            request.headers.get(REQUEST_ID_HEADER)
            or str(uuid.uuid4())
        )
        request.state.request_id = request_id

        start = time.perf_counter()
        response = await call_next(request)

        response.headers[REQUEST_ID_HEADER] = request_id

        logger.info(
            "request_completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(
                    (time.perf_counter() - start) * 1000, 2
                ),
            },
        )

        return response

    @api.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request,
        exc: RequestValidationError,
    ):
        details = [
            {
                "field": ".".join(str(part) for part in item["loc"]),
                "message": item["msg"],
            }
            for item in exc.errors()
        ]

        return error_response(
            422,
            "VALIDATION_ERROR",
            "Request validation failed",
            request,
            details,
        )

    @api.exception_handler(StarletteHTTPException)
    async def http_error_handler(
        request: Request,
        exc: StarletteHTTPException,
    ):
        code = {
            404: "NOT_FOUND",
            409: "CONFLICT",
        }.get(exc.status_code, "HTTP_ERROR")

        return error_response(
            exc.status_code,
            code,
            str(exc.detail),
            request,
        )

    @api.get("/health", tags=["operations"])
    def health():
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "ok",
            "service": "show-service",
        }

    api.include_router(router)

    return api


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("SHOW_PORT", "8002")),
    )