from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl, BaseSettings, validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    APP_NAME: str = "Job Automation Backend"
    DEBUG: bool = False

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./job_automation.db"

    # Redis / Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str | None = None
    CELERY_RESULT_BACKEND: str | None = None

    @validator("CELERY_BROKER_URL", always=True)
    def default_celery_broker_url(cls, v: str | None, values: dict) -> str:
        return v or values.get("REDIS_URL", "redis://localhost:6379/0")

    @validator("CELERY_RESULT_BACKEND", always=True)
    def default_celery_result_backend(cls, v: str | None, values: dict) -> str:
        return v or values.get("REDIS_URL", "redis://localhost:6379/0")

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()

