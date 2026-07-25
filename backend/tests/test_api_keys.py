"""API key management + public (key-authenticated) read API tests."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.conftest import make_user

KEYS = "/api/v1/keys"
PUBLIC = "/api/v1/public"
PROMPTS = "/api/v1/prompts"


def _prompt_payload(**over) -> dict:
    base = {
        "title": "Public API Sample Prompt",
        "description": "A prompt to expose over the public API",
        "content": "Build a REST endpoint that...",
        "prompt_type": "backend",
        "status": "published",
    }
    base.update(over)
    return base


async def _mint_key(client: AsyncClient, headers: dict, name: str = "CLI") -> tuple[str, dict]:
    resp = await client.post(KEYS, json={"name": name}, headers=headers)
    assert resp.status_code == 201, resp.text
    body = resp.json()
    return body["key"], body


@pytest.mark.asyncio
async def test_create_key_returns_secret_once(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    full_key, body = await _mint_key(client, headers)

    assert full_key.startswith("pf_")
    assert body["prefix"] and full_key.startswith(body["prefix"])
    assert body["revoked_at"] is None

    # Listing never leaks the secret.
    listed = (await client.get(KEYS, headers=headers)).json()
    assert len(listed) == 1
    assert "key" not in listed[0]
    assert listed[0]["prefix"] == body["prefix"]


@pytest.mark.asyncio
async def test_public_me_requires_and_accepts_key(client: AsyncClient) -> None:
    me, headers = await make_user(client)
    full_key, _ = await _mint_key(client, headers)

    # No key -> 401
    assert (await client.get(f"{PUBLIC}/me")).status_code == 401
    # Garbage key -> 401
    bad = await client.get(f"{PUBLIC}/me", headers={"X-API-Key": "pf_notreal"})
    assert bad.status_code == 401

    ok = await client.get(f"{PUBLIC}/me", headers={"X-API-Key": full_key})
    assert ok.status_code == 200
    assert ok.json()["username"] == me["username"]


@pytest.mark.asyncio
async def test_public_prompts_list_and_detail(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    full_key, _ = await _mint_key(client, headers)
    prompt = (await client.post(PROMPTS, json=_prompt_payload(), headers=headers)).json()

    key_headers = {"X-API-Key": full_key}
    listing = await client.get(f"{PUBLIC}/prompts", headers=key_headers)
    assert listing.status_code == 200
    assert any(p["id"] == prompt["id"] for p in listing.json()["items"])

    detail = await client.get(f"{PUBLIC}/prompts/{prompt['id']}", headers=key_headers)
    assert detail.status_code == 200
    assert detail.json()["content"] == _prompt_payload()["content"]

    # The public list requires a key.
    assert (await client.get(f"{PUBLIC}/prompts")).status_code == 401


@pytest.mark.asyncio
async def test_public_api_hides_drafts(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    full_key, _ = await _mint_key(client, headers)
    draft = (
        await client.post(PROMPTS, json=_prompt_payload(status="draft"), headers=headers)
    ).json()

    key_headers = {"X-API-Key": full_key}
    listing = (await client.get(f"{PUBLIC}/prompts", headers=key_headers)).json()
    assert all(p["id"] != draft["id"] for p in listing["items"])

    detail = await client.get(f"{PUBLIC}/prompts/{draft['id']}", headers=key_headers)
    assert detail.status_code == 404


@pytest.mark.asyncio
async def test_public_api_hides_private_team_prompts(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    full_key, _ = await _mint_key(client, headers)
    team = (
        await client.post("/api/v1/teams", json={"name": "Squad"}, headers=headers)
    ).json()
    private = (
        await client.post(
            PROMPTS, json=_prompt_payload(team_id=team["id"]), headers=headers
        )
    ).json()

    key_headers = {"X-API-Key": full_key}
    listing = (await client.get(f"{PUBLIC}/prompts", headers=key_headers)).json()
    assert all(p["id"] != private["id"] for p in listing["items"])
    detail = await client.get(f"{PUBLIC}/prompts/{private['id']}", headers=key_headers)
    assert detail.status_code == 404


@pytest.mark.asyncio
async def test_revoked_key_stops_working(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    full_key, body = await _mint_key(client, headers)
    key_headers = {"X-API-Key": full_key}

    assert (await client.get(f"{PUBLIC}/me", headers=key_headers)).status_code == 200

    revoke = await client.delete(f"{KEYS}/{body['id']}", headers=headers)
    assert revoke.status_code == 204

    assert (await client.get(f"{PUBLIC}/me", headers=key_headers)).status_code == 401
    # Still listed, now marked revoked.
    listed = (await client.get(KEYS, headers=headers)).json()
    assert listed[0]["revoked_at"] is not None


@pytest.mark.asyncio
async def test_cannot_revoke_another_users_key(client: AsyncClient) -> None:
    _, alice = await make_user(client)
    _, bob = await make_user(client)
    _, body = await _mint_key(client, alice)

    resp = await client.delete(f"{KEYS}/{body['id']}", headers=bob)
    assert resp.status_code == 404
