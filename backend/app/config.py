"""Application settings, read from environment variables (12-factor style).

The database connection can be supplied either as one DATABASE_URL or as the
individual DB_* parts. Kubernetes uses the parts so the password can come from a
Secret without being embedded in a connection string.
"""

from functools import lru_cache
from urllib.parse import quote_plus

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "ShelfLife API"
    # Set at image build time from the Git commit SHA so the UI can show what is deployed.
    app_version: str = "dev"
    environment: str = "local"

    database_url: str | None = None
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "shelflife"
    db_user: str = "shelflife"
    db_password: str = ""

    # Items expiring within this many days are flagged as "expiring soon".
    expiry_warning_days: int = Field(default=3, ge=0, le=60)
    # "Today" is evaluated in this timezone, so expiry status does not flip at UTC midnight.
    app_timezone: str = "Asia/Kolkata"

    # Comma-separated list. Only needed when the UI is served from a different origin
    # (e.g. the Vite dev server). Docker/Kubernetes serve UI and API from one origin.
    cors_origins: str = "http://localhost:5173"

    # How long the container start-up script waits for PostgreSQL before giving up.
    db_wait_seconds: int = 60

    @property
    def sqlalchemy_url(self) -> str:
        if self.database_url:
            return self.database_url
        password = quote_plus(self.db_password)
        return f"postgresql+psycopg://{self.db_user}:{password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
