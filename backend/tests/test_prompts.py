"""Prompt CRUD, versioning, copy, and fork tests."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.conftest import make_user

PROMPTS = "/api/v1/prompts"


def _prompt_payload(**over) -> dict:
    base = {
        "title": "Modern Glassmorphism Login",
        "description": "A sleek glass login form",
        "content": "Build a login page with glassmorphism styling...",
        "prompt_type": "ui",
        "complexity": "intermediate",
        "framework": "React",
        "language": "TypeScript",
        "ai_model": "claude-opus-4-8",
        "status": "published",
    }
    base.update(over)
    return base


async def _create(client: AsyncClient, headers: dict, **over) -> dict:
    resp = await client.post(PROMPTS, json=_prompt_payload(**over), headers=headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


@pytest.mark.asyncio
async def test_create_prompt_seeds_version_one(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    prompt = await _create(client, headers)
    assert prompt["current_version"] == 1
    assert prompt["slug"].startswith("modern-glassmorphism-login-")
    assert prompt["author"]["username"].startswith("user")

    versions = (await client.get(f"{PROMPTS}/{prompt['id']}/versions")).json()
    assert len(versions) == 1
    assert versions[0]["version_number"] == 1
    assert versions[0]["change_summary"] == "Initial version"


@pytest.mark.asyncio
async def test_create_requires_auth(client: AsyncClient) -> None:
    resp = await client.post(PROMPTS, json=_prompt_payload())
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_prompt_increments_views(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    prompt = await _create(client, headers)
    first = (await client.get(f"{PROMPTS}/{prompt['id']}")).json()
    second = (await client.get(f"{PROMPTS}/{prompt['id']}")).json()
    assert second["views_count"] == first["views_count"] + 1


@pytest.mark.asyncio
async def test_add_version_advances_snapshot(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    prompt = await _create(client, headers)

    resp = await client.post(
        f"{PROMPTS}/{prompt['id']}/versions",
        json={"content": "v2 content", "change_summary": "Add dark mode"},
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json()["version_number"] == 2

    detail = (await client.get(f"{PROMPTS}/{prompt['id']}")).json()
    assert detail["current_version"] == 2
    assert detail["content"] == "v2 content"

    versions = (await client.get(f"{PROMPTS}/{prompt['id']}/versions")).json()
    assert [v["version_number"] for v in versions] == [2, 1]  # newest first


@pytest.mark.asyncio
async def test_only_owner_or_mod_can_edit(client: AsyncClient) -> None:
    _, owner = await make_user(client)
    _, other = await make_user(client)
    prompt = await _create(client, owner)

    resp = await client.patch(
        f"{PROMPTS}/{prompt['id']}", json={"title": "Hijacked"}, headers=other
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_metadata_patch_does_not_bump_version(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    prompt = await _create(client, headers)
    resp = await client.patch(
        f"{PROMPTS}/{prompt['id']}", json={"title": "Renamed"}, headers=headers
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Renamed"
    assert resp.json()["current_version"] == 1


@pytest.mark.asyncio
async def test_copy_increments_copies(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    prompt = await _create(client, headers)
    resp = await client.post(f"{PROMPTS}/{prompt['id']}/copy")
    assert resp.status_code == 200
    body = resp.json()
    assert body["copies_count"] == 1
    assert body["content"] == _prompt_payload()["content"]


@pytest.mark.asyncio
async def test_fork_creates_draft_owned_by_forker(client: AsyncClient) -> None:
    _, owner = await make_user(client)
    forker, forker_h = await make_user(client)
    prompt = await _create(client, owner)

    resp = await client.post(f"{PROMPTS}/{prompt['id']}/fork", headers=forker_h)
    assert resp.status_code == 201
    fork = resp.json()
    assert fork["forked_from_id"] == prompt["id"]
    assert fork["status"] == "draft"
    assert fork["author"]["id"] == forker["id"]
    assert fork["id"] != prompt["id"]

    source = (await client.get(f"{PROMPTS}/{prompt['id']}")).json()
    assert source["forks_count"] == 1


@pytest.mark.asyncio
async def test_search_filters_and_sorts(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    await _create(client, headers, title="React Dashboard", framework="React")
    await _create(client, headers, title="Vue Landing", framework="Vue")

    # Filter by framework
    resp = await client.get(PROMPTS, params={"framework": "Vue"})
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "Vue Landing"

    # Full-text-ish search
    resp = await client.get(PROMPTS, params={"q": "dashboard"})
    assert resp.json()["total"] == 1


@pytest.mark.asyncio
async def test_delete_prompt(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    prompt = await _create(client, headers)
    resp = await client.delete(f"{PROMPTS}/{prompt['id']}", headers=headers)
    assert resp.status_code == 204
    assert (await client.get(f"{PROMPTS}/{prompt['id']}")).status_code == 404


@pytest.mark.asyncio
async def test_list_excludes_drafts_by_default(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    await _create(client, headers, title="Published One", status="published")
    await _create(client, headers, title="Draft One", status="draft")

    resp = await client.get(PROMPTS, params={"q": "One"})
    titles = [p["title"] for p in resp.json()["items"]]
    assert "Published One" in titles
    assert "Draft One" not in titles
