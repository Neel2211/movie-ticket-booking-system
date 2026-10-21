from fastapi import FastAPI
from app.database import engine, Base
from app.routes import notifications

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Notification Service",
    description="Shared mock microservice responsible for dispatching email and SMS alerts.",
    version="1.0.0"
)

app.include_router(notifications.router)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "notification-service"}