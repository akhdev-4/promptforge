"""Pytest fixtures.

Tests run against an isolated in-memory SQLite database and an ASGI transport
so no network or external services are required.
"""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("AUTO_CREATE_TABLES", "false")

import pytest_asyncio  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.db.base import Base  # noqa: E402
from app.db.session import get_db  # noqa: E402
from app.main import app  # noqa: E402

# One shared in-memory engine for the whole test session.
_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
)
_TestSession = async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def _create_schema() -> AsyncGenerator[None, None]:
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await _engine.dispose()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with _TestSession() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# --- Auth helpers -----------------------------------------------------------
_user_counter = 0


async def make_user(
    client: AsyncClient, *, role: str | None = None
) -> tuple[dict, dict[str, str]]:
    """Register + log in a unique user. Returns (user, auth_headers)."""
    global _user_counter
    _user_counter += 1
    email = f"user{_user_counter}@test.io"
    username = f"user{_user_counter}"
    password = "password123"

    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "username": username},
    )
    tokens = (
        await client.post(
            "/api/v1/auth/login", data={"username": email, "password": password}
        )
    ).json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    me = (await client.get("/api/v1/users/me", headers=headers)).json()
    return me, headers
