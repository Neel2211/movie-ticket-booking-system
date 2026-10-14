from fastapi import FastAPI
from app.database import engine, Base
from app.routes import payments

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Payment Service",
    description="Microservice responsible for processing transactions securely and idempotently.",
    version="1.0.0"
)

app.include_router(payments.router)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "payment-service"}