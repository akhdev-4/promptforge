"""Auth flow tests: register, login, refresh, me, guards."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

REGISTER = "/api/v1/auth/register"
LOGIN = "/api/v1/auth/login"
REFRESH = "/api/v1/auth/refresh"
ME = "/api/v1/users/me"


async def _register(client: AsyncClient, **over) -> dict:
    payload = {
        "email": over.get("email", "dev@promptforge.io"),
        "password": over.get("password", "supersecret1"),
        "username": over.get("username", "dev"),
        "full_name": "Dev User",
    }
    resp = await client.post(REGISTER, json=payload)
    return resp


async def _login_tokens(client: AsyncClient, email: str, password: str) -> dict:
    resp = await client.post(LOGIN, data={"username": email, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()


@pytest.mark.asyncio
async def test_register_returns_user_with_role(client: AsyncClient) -> None:
    resp = await _register(client, email="a@x.io", username="alice")
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["email"] == "a@x.io"
    assert body["role"] == "contributor"
    assert "password" not in body and "hashed_password" not in body


@pytest.mark.asyncio
async def test_register_duplicate_email_conflicts(client: AsyncClient) -> None:
    await _register(client, email="dupe@x.io", username="dupe1")
    resp = await _register(client, email="dupe@x.io", username="dupe2")
    assert resp.status_code == 409
    assert resp.json()["code"] == "conflict"


@pytest.mark.asyncio
async def test_login_and_access_me(client: AsyncClient) -> None:
    await _register(client, email="log@x.io", username="logger", password="password123")
    tokens = await _login_tokens(client, "log@x.io", "password123")
    assert tokens["token_type"] == "bearer"

    resp = await client.get(ME, headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "log@x.io"


@pytest.mark.asyncio
async def test_login_wrong_password_401(client: AsyncClient) -> None:
    await _register(client, email="wp@x.io", username="wpuser", password="password123")
    resp = await client.post(LOGIN, data={"username": "wp@x.io", "password": "nope"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_requires_auth(client: AsyncClient) -> None:
    resp = await client.get(ME)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh_issues_new_tokens(client: AsyncClient) -> None:
    await _register(client, email="rf@x.io", username="rfuser", password="password123")
    tokens = await _login_tokens(client, "rf@x.io", "password123")
    resp = await client.post(REFRESH, json={"refresh_token": tokens["refresh_token"]})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_access_token_rejected_as_refresh(client: AsyncClient) -> None:
    await _register(client, email="tt@x.io", username="ttuser", password="password123")
    tokens = await _login_tokens(client, "tt@x.io", "password123")
    resp = await client.post(REFRESH, json={"refresh_token": tokens["access_token"]})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_admin_only_list_forbidden_for_contributor(client: AsyncClient) -> None:
    await _register(client, email="c@x.io", username="contrib", password="password123")
    tokens = await _login_tokens(client, "c@x.io", "password123")
    resp = await client.get(
        "/api/v1/users", headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    assert resp.status_code == 403
    assert resp.json()["code"] == "permission_denied"
