from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str = ""
    OPENAI_API_KEY: str = ""
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/autoad"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
