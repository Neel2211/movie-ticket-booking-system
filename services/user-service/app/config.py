"""Configuration, read only from environment variables."""
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    service_name: str
    port: int
    database_url: str
    log_level: str


def get_settings() -> Settings:
    return Settings(
        service_name=os.getenv("SERVICE_NAME", "user-service"),
        port=int(os.getenv("PORT", "8001")),
        database_url=os.getenv("DATABASE_URL", "sqlite:///./user_service.db"),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
    )
