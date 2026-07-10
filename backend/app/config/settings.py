import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "InfraMind AI"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = Field(default="SUPER_SECRET_KEY_FOR_INFRAMIND_AI_1234567890", validation_alias="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week
    
    # Database configuration (PostgreSQL/TimescaleDB)
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/inframind_db",
        validation_alias="DATABASE_URL"
    )
    
    # Cache & Task Queue
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        validation_alias="REDIS_URL"
    )
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/0",
        validation_alias="CELERY_BROKER_URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/0",
        validation_alias="CELERY_RESULT_BACKEND"
    )
    
    # Gemini API Key
    GEMINI_API_KEY: str = Field(
        default="",
        validation_alias="GEMINI_API_KEY"
    )
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
