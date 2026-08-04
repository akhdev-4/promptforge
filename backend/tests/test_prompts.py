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


@pytest.mark.asyncio
async def test_version_history_names_its_author(client: AsyncClient) -> None:
    author, author_headers = await make_user(client)
    forker, forker_headers = await make_user(client)
    prompt = await _create(client, author_headers)

    fork = (
        await client.post(f"{PROMPTS}/{prompt['id']}/fork", headers=forker_headers)
    ).json()

    versions = (await client.get(f"{PROMPTS}/{fork['id']}/versions")).json()
    v1 = versions[0]
    # The fork's v1 is credited to whoever forked it...
    assert v1["author"]["username"] == forker["username"]
    # ...and the note points back at the original and its author.
    assert prompt["title"] in v1["change_summary"]
    assert author["username"] in v1["change_summary"]

    # A later version is credited to whoever wrote it.
    await client.post(
        f"{PROMPTS}/{fork['id']}/versions",
        json={"content": "Reworked for Vue.", "change_summary": "Port to Vue"},
        headers=forker_headers,
    )
    latest = (await client.get(f"{PROMPTS}/{fork['id']}/versions")).json()[0]
    assert latest["version_number"] == 2
    assert latest["author"]["username"] == forker["username"]


@pytest.mark.asyncio
async def test_drafts_are_private_to_their_author(client: AsyncClient) -> None:
    _, mine = await make_user(client)
    _, theirs = await make_user(client)
    draft = await _create(client, mine, title="My unfinished idea", status="draft")

    # Anonymous callers can't browse unpublished prompts at all.
    assert (await client.get(f"{PROMPTS}?status=draft")).status_code == 401

    # Another signed-in user sees their own drafts, never yours.
    others = await client.get(f"{PROMPTS}?status=draft", headers=theirs)
    assert others.status_code == 200
    assert all(p["id"] != draft["id"] for p in others.json()["items"])

    # The author does see it.
    ours = await client.get(f"{PROMPTS}?status=draft", headers=mine)
    assert any(p["id"] == draft["id"] for p in ours.json()["items"])

    # And it stays out of the public library.
    public = await client.get(f"{PROMPTS}?q=My unfinished idea")
    assert all(p["id"] != draft["id"] for p in public.json()["items"])


@pytest.mark.asyncio
async def test_fork_starts_as_a_draft(client: AsyncClient) -> None:
    _, author = await make_user(client)
    _, forker = await make_user(client)
    prompt = await _create(client, author)

    fork = (
        await client.post(f"{PROMPTS}/{prompt['id']}/fork", headers=forker)
    ).json()
    # Explains the "my fork vanished" report: it's a draft, so the library hides it.
    assert fork["status"] == "draft"


@pytest.mark.asyncio
async def test_open_prompts_accept_contributions_from_anyone(client: AsyncClient) -> None:
    owner_me, owner = await make_user(client)
    helper_me, helper = await make_user(client)

    prompt = await _create(client, owner, title="Open for improvement")
    # Closed by default: a stranger can't touch it.
    closed = await client.post(
        f"{PROMPTS}/{prompt['id']}/versions",
        json={"content": "better wording"},
        headers=helper,
    )
    assert closed.status_code == 403

    # The owner opens it up.
    await client.patch(
        f"{PROMPTS}/{prompt['id']}",
        json={"allow_contributions": True},
        headers=owner,
    )

    opened = await client.post(
        f"{PROMPTS}/{prompt['id']}/versions",
        json={"content": "better wording", "change_summary": "Clarified the constraints"},
        headers=helper,
    )
    assert opened.status_code == 201, opened.text

    # One prompt, two names in its history.
    versions = (await client.get(f"{PROMPTS}/{prompt['id']}/versions")).json()
    assert versions[0]["author"]["username"] == helper_me["username"]
    assert versions[1]["author"]["username"] == owner_me["username"]

    # The detail payload tells each viewer whether they may contribute.
    as_helper = (await client.get(f"{PROMPTS}/{prompt['id']}", headers=helper)).json()
    assert as_helper["allow_contributions"] is True
    assert as_helper["can_contribute"] is True
    anon = (await client.get(f"{PROMPTS}/{prompt['id']}")).json()
    assert anon["can_contribute"] is False
