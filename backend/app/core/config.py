from pydantic_settings import BaseSettings
from functools import lru_cache
import os
import json


class Settings(BaseSettings):
    APP_NAME: str = "极米售后AI助手 API"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./chatbot.db"

    # Redis (optional for local dev)
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET: str = "dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 480

    # LLM
    LLM_MODE: str = "mock"  # "mock" | "deepseek"
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    # ChromaDB
    CHROMA_PATH: str = "./chroma_data"

    # CORS
    CORS_ORIGINS: str = '["http://localhost:5173", "http://localhost:3000"]'

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def get_cors_origins(self) -> list[str]:
        """Parse CORS_ORIGINS from JSON string or comma-separated list."""
        raw = self.CORS_ORIGINS
        if isinstance(raw, list):
            return raw
        if isinstance(raw, str):
            try:
                return json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                # Fallback: comma-separated
                return [o.strip() for o in raw.split(",") if o.strip()]
        return ["*"]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
