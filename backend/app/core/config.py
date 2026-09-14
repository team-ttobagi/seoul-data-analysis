from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    PROJECT_NAME: str = "SEOUL DATA PLAYGROUND API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite+aiosqlite:///./seouldata.db"
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    CORS_ORIGINS: str = (
        "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000"
    )
    ENVIRONMENT: str = "development"

    SEOUL_API_KEY: str = ""
    SEOUL_API_BASE_URL: str = "http://openapi.seoul.go.kr:8088"

    GEMINI_ENABLED: bool = False
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.1-flash-lite"
    GEMINI_TIMEOUT_SECONDS: float = Field(default=6.0, ge=2.0, le=10)
    GEMINI_MAX_RETRIES: int = Field(default=2, ge=0, le=2)
    GEMINI_MAX_CONCURRENT_REQUESTS: int = Field(default=2, ge=1, le=10)
    GEMINI_MIN_REQUEST_INTERVAL_SECONDS: float = Field(default=0.1, ge=0.0, le=60.0)

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    @property
    def cors_origins_list(self) -> List[str]:
        return [
            origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()
        ]


settings = Settings()
