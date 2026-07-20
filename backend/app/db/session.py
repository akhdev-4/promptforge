"""Async database engine and session management."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

# SQLite needs check_same_thread disabled for the async driver; Postgres pools
# connections normally. We branch on the resolved URL so both "just work".
_engine_kwargs: dict = {"echo": settings.DB_ECHO, "future": True}
if settings.is_sqlite:
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    _engine_kwargs.update(pool_size=10, max_overflow=20, pool_pre_ping=True)
    # Managed Postgres (Neon/Supabase) requires TLS; asyncpg takes it here since
    # the libpq-style sslmode query param is stripped from the URL.
    if settings.db_requires_ssl:
        _engine_kwargs["connect_args"] = {"ssl": True}

engine = create_async_engine(settings.sqlalchemy_database_uri, **_engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding a transactional session.

    Commits on success, rolls back on exception, and always closes.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
