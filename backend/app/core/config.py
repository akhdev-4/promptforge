"""Application configuration.

All settings are sourced from environment variables (or a local ``.env`` file)
via ``pydantic-settings``. This keeps the codebase 12-factor compliant and lets
the same image run against SQLite locally and PostgreSQL in production by
changing a single variable.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated, Literal

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # --- Core -----------------------------------------------------------------
    PROJECT_NAME: str = "PromptForge"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: Literal["local", "development", "staging", "production"] = "local"
    DEBUG: bool = True

    # --- Security -------------------------------------------------------------
    # Override in production. Generate with: openssl rand -hex 32
    SECRET_KEY: str = "CHANGE_ME_dev_secret_key_do_not_use_in_production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ALGORITHM: str = "HS256"

    # --- Database -------------------------------------------------------------
    # If DATABASE_URL is unset we fall back to a local SQLite file so the app
    # runs with zero external dependencies. Set to a postgresql+asyncpg URL for
    # production, e.g. postgresql+asyncpg://user:pass@localhost:5432/promptforge
    DATABASE_URL: str | None = None
    SQLITE_PATH: str = "./promptforge.db"
    DB_ECHO: bool = False
    # Create tables on startup (handy for SQLite dev). Use Alembic in production.
    AUTO_CREATE_TABLES: bool = True

    # --- Cache / Queue --------------------------------------------------------
    REDIS_URL: str = "redis://localhost:6379/0"

    # --- CORS -----------------------------------------------------------------
    # NoDecode: skip pydantic-settings' JSON decoding of this list field so the
    # validator below can accept a plain comma-separated env value.
    BACKEND_CORS_ORIGINS: Annotated[list[AnyHttpUrl | str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000"]
    )

    # --- Pagination -----------------------------------------------------------
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # --- Playground (prompt runner) -------------------------------------------
    # "mock" = zero-key demo output. "gemini" = real output via Google's free
    # tier (get a key at aistudio.google.com, no card needed) — set GEMINI_API_KEY.
    LLM_PROVIDER: Literal["mock", "gemini"] = "mock"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-flash-latest"
    PLAYGROUND_MAX_TOKENS: int = 8192  # room for full code output without truncation

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def _split_cors(cls, value: object) -> object:
        if isinstance(value, str) and not value.startswith("["):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def sqlalchemy_database_uri(self) -> str:
        """Resolved DB URL, normalized for the async driver.

        Managed Postgres providers (Neon, Supabase, Railway) hand out URLs like
        ``postgres://…?sslmode=require``. We normalize the scheme to
        ``postgresql+asyncpg://`` and strip libpq-only query params that asyncpg
        can't parse (SSL is applied via connect_args — see ``db_requires_ssl``).
        """
        url = self.DATABASE_URL
        if not url:
            return f"sqlite+aiosqlite:///{self.SQLITE_PATH}"

        if url.startswith("postgres://"):
            url = "postgresql://" + url.split("://", 1)[1]
        if url.startswith("postgresql://"):
            url = "postgresql+asyncpg://" + url.split("://", 1)[1]
        if "+asyncpg://" in url and "?" in url:
            url = url.split("?", 1)[0]
        return url

    @property
    def is_sqlite(self) -> bool:
        return self.sqlalchemy_database_uri.startswith("sqlite")

    @property
    def db_requires_ssl(self) -> bool:
        """True when the source URL asked for TLS (e.g. Neon's sslmode=require)."""
        raw = (self.DATABASE_URL or "").lower()
        return "sslmode=require" in raw or "ssl=true" in raw


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
