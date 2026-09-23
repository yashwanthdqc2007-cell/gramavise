from pathlib import Path
from typing import Any, List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator, model_validator

# Compute absolute path to backend directory
_BACKEND_DIR = Path(__file__).resolve().parent.parent
_DEFAULT_SQLITE_PATH = (_BACKEND_DIR / "gramavise_dev.db").as_posix()
_DEFAULT_DATABASE_URL = f"sqlite:///{_DEFAULT_SQLITE_PATH}"


class Settings(BaseSettings):
    """Application configuration settings loaded from environment variables."""

    # Application Meta
    APP_NAME: str = "GramaVise Backend"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"  # development, staging, production, test
    DEBUG: bool = True
    SECRET_KEY: str = "default_insecure_secret_key_for_development"

    # Server Configuration
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    # Request Protection & Security Limits
    MAX_REQUEST_SIZE_BYTES: int = 1_048_576  # 1 MB default maximum body size

    # Structured Logging
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR

    # Database Configuration (PostgreSQL in production, SQLite in development/test)
    DATABASE_URL: str = Field(
        default=_DEFAULT_DATABASE_URL,
        description="SQLAlchemy database connection URI (e.g. postgresql://user:pass@localhost:5432/gramavise)"
    )

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, v: Union[str, Any]) -> str:
        if isinstance(v, str) and v.startswith("sqlite:///./"):
            relative_file = v.replace("sqlite:///./", "")
            resolved_path = (_BACKEND_DIR / relative_file).as_posix()
            return f"sqlite:///{resolved_path}"
        return v
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800

    # AI & LLM Provider Configuration
    LLM_PROVIDER: str = "mock"  # Options: mock, openai, anthropic, gemini
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gemini-1.5-flash"
    LLM_TEMPERATURE: float = 0.2

    # OpenStreetMap / Geospatial
    OSM_API_URL: str = "https://nominatim.openstreetmap.org"
    OVERPASS_API_URL: str = "https://overpass-api.de/api/interpreter"
    GEO_USER_AGENT: str = "GramaVise-Rural-Business-Advisor/1.0"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            # Support comma-separated string format from environment variables
            v_clean = v.strip()
            if not v_clean:
                return []
            if v_clean.startswith("[") and v_clean.endswith("]"):
                import json
                try:
                    return json.loads(v_clean)
                except Exception:
                    pass
            return [origin.strip() for origin in v_clean.split(",") if origin.strip()]
        return v

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        """Prevent development security defaults from being used in production."""
        if self.ENVIRONMENT.lower() == "production":
            if self.DEBUG:
                raise ValueError("DEBUG must be False when ENVIRONMENT is production")
            if not self.SECRET_KEY or self.SECRET_KEY == "default_insecure_secret_key_for_development":
                raise ValueError("A non-default SECRET_KEY is required when ENVIRONMENT is production")
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
