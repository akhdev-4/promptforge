"""Email verification and password reset flows."""

from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.models.auth_token import AuthToken, TokenPurpose
from tests.conftest import make_user

AUTH = "/api/v1/auth"


# Tokens only ever leave the system by email, and just their digest is stored —
# so tests mint one through the service and keep the returned raw value.


@pytest.mark.asyncio
async def test_verify_email_flow(client: AsyncClient, db_session: AsyncSession) -> None:
    from app.repositories.user import UserRepository
    from app.services.account import AccountService

    me, headers = await make_user(client)
    user = await UserRepository(db_session).get_by_email(me["email"])
    assert user is not None and user.is_verified is False

    # Mint a link the way registration does; capture the raw token.
    service = AccountService(db_session)
    raw = await service._issue(
        user, TokenPurpose.EMAIL_VERIFY, __import__("datetime").timedelta(hours=1)
    )
    await db_session.commit()

    resp = await client.post(f"{AUTH}/verify-email?token={raw}")
    assert resp.status_code == 200, resp.text
    assert resp.json()["is_verified"] is True

    # Single use: the same link can't be replayed.
    again = await client.post(f"{AUTH}/verify-email?token={raw}")
    assert again.status_code == 409


@pytest.mark.asyncio
async def test_verify_rejects_unknown_token(client: AsyncClient) -> None:
    resp = await client.post(f"{AUTH}/verify-email?token=not-a-real-token")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_forgot_password_does_not_leak_accounts(client: AsyncClient) -> None:
    me, _ = await make_user(client)
    known = await client.post(f"{AUTH}/forgot-password", json={"email": me["email"]})
    unknown = await client.post(
        f"{AUTH}/forgot-password", json={"email": "nobody@example.com"}
    )
    assert known.status_code == unknown.status_code == 200
    # Identical wording either way — no account enumeration.
    assert known.json()["detail"] == unknown.json()["detail"]


@pytest.mark.asyncio
async def test_password_reset_changes_password(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    from app.repositories.user import UserRepository
    from app.services.account import AccountService

    me, _ = await make_user(client)
    user = await UserRepository(db_session).get_by_email(me["email"])
    assert user is not None

    service = AccountService(db_session)
    raw = await service._issue(
        user, TokenPurpose.PASSWORD_RESET, __import__("datetime").timedelta(minutes=30)
    )
    await db_session.commit()

    resp = await client.post(
        f"{AUTH}/reset-password", json={"token": raw, "password": "brand-new-pass-1"}
    )
    assert resp.status_code == 200, resp.text
    assert "access_token" in resp.json()  # signed straight in

    # The new password works, the old one doesn't.
    ok = await client.post(
        f"{AUTH}/login", data={"username": me["email"], "password": "brand-new-pass-1"}
    )
    assert ok.status_code == 200
    stale = await client.post(
        f"{AUTH}/login", data={"username": me["email"], "password": "password123"}
    )
    assert stale.status_code == 401

    # Reset links are single-use.
    replay = await client.post(
        f"{AUTH}/reset-password", json={"token": raw, "password": "another-pass-99"}
    )
    assert replay.status_code == 409


@pytest.mark.asyncio
async def test_issuing_a_token_invalidates_the_previous_one(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    from datetime import timedelta

    from app.repositories.user import UserRepository
    from app.services.account import AccountService

    me, _ = await make_user(client)
    user = await UserRepository(db_session).get_by_email(me["email"])
    assert user is not None

    service = AccountService(db_session)
    first = await service._issue(user, TokenPurpose.EMAIL_VERIFY, timedelta(hours=1))
    second = await service._issue(user, TokenPurpose.EMAIL_VERIFY, timedelta(hours=1))
    await db_session.commit()

    # Requesting a new link retires the old one.
    stale = await client.post(f"{AUTH}/verify-email?token={first}")
    assert stale.status_code == 409
    fresh = await client.post(f"{AUTH}/verify-email?token={second}")
    assert fresh.status_code == 200

    # Only the digest is stored — never the token itself.
    rows = (
        await db_session.execute(
            select(AuthToken).where(AuthToken.user_id == user.id)
        )
    ).scalars().all()
    assert all(r.hashed_token != second for r in rows)
    assert any(r.hashed_token == security.hash_api_key(second) for r in rows)
