"""Application configuration from environment."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings loaded from env vars."""

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/autoad"

    # JWT
    JWT_SECRET_KEY: str = "change-me-in-production-use-long-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Default admin (used by migrations/seeding)
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
