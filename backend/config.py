import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    database_url: str = os.getenv("DATABASE_URL", "")
    better_auth_secret: str = os.getenv("BETTER_AUTH_SECRET", "")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    openrouter_model: str = os.getenv("OPENROUTER_MODEL", "qwen/qwen3-next-80b-a3b-instruct:free")
    app_url: str = os.getenv("APP_URL", "http://localhost:3000")
    app_title: str = os.getenv("APP_TITLE", "Todo App AI Chatbot")

    class Config:
        env_file = ".env"


# Create a single instance of settings
settings = Settings()