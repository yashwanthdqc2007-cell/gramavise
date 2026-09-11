from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application configuration settings loaded from environment variables."""

    # Application Meta
    APP_NAME: str = "GramaVise Backend"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "default_insecure_secret_key_for_development"

    # Server Configuration
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
    ]

    # Database Configuration (PostgreSQL)
    # Default to an in-memory SQLite if PostgreSQL is unavailable in local dev
    DATABASE_URL: str = Field(
        default="sqlite:///./gramavise_dev.db",
        description="SQLAlchemy database connection URI (e.g. postgresql://user:pass@localhost:5432/gramavise)"
    )

    # AI & LLM Provider Configuration
    LLM_PROVIDER: str = "mock"  # Options: mock, openai, anthropic, gemini
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gemini-1.5-flash"
    LLM_TEMPERATURE: float = 0.2

    # OpenStreetMap / Geospatial
    OSM_API_URL: str = "https://nominatim.openstreetmap.org"
    OVERPASS_API_URL: str = "https://overpass-api.de/api/interpreter"
    GEO_USER_AGENT: str = "GramaVise-Rural-Business-Advisor/1.0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
