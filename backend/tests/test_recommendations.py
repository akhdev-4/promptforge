"""Related-prompt recommendation tests."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.conftest import make_user

PROMPTS = "/api/v1/prompts"
RECS = "/api/v1/users/me/recommendations"


async def _create(client: AsyncClient, headers: dict, **over) -> dict:
    payload = {
        "title": "P",
        "content": "...",
        "prompt_type": "ui",
        "complexity": "intermediate",
        "status": "published",
    }
    payload.update(over)
    return (await client.post(PROMPTS, json=payload, headers=headers)).json()


@pytest.mark.asyncio
async def test_related_ranks_shared_tags_first(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    source = await _create(client, headers, title="Source", tags=["auth", "login", "glass"])
    await _create(client, headers, title="Strong", tags=["auth", "login"])
    await _create(client, headers, title="Weak", tags=["auth"])
    await _create(client, headers, title="Unrelated", prompt_type="backend")

    related = (await client.get(f"{PROMPTS}/{source['id']}/related")).json()
    titles = [p["title"] for p in related]

    assert "Source" not in titles  # never recommends itself
    # More shared tags → ranked higher.
    assert titles.index("Strong") < titles.index("Weak")


@pytest.mark.asyncio
async def test_related_excludes_self_and_limits(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    source = await _create(client, headers, title="Src", tags=["x"])
    for i in range(8):
        await _create(client, headers, title=f"C{i}", tags=["x"])

    related = (await client.get(f"{PROMPTS}/{source['id']}/related", params={"limit": 3})).json()
    assert len(related) == 3
    assert all(p["id"] != source["id"] for p in related)


@pytest.mark.asyncio
async def test_feed_personalizes_from_bookmarks(client: AsyncClient) -> None:
    _, author = await make_user(client)
    # A prompt the reader will bookmark, and a strong match sharing its tags.
    seed = await _create(client, author, title="Glass Login", tags=["auth", "login", "glass"])
    match = await _create(client, author, title="Glass Signup", tags=["auth", "login", "glass"])
    await _create(client, author, title="Unrelated", prompt_type="backend", tags=["ops"])

    _, reader = await make_user(client)
    resp = await client.post(f"{PROMPTS}/{seed['id']}/bookmark", headers=reader)
    assert resp.status_code == 200, resp.text

    recs = (await client.get(RECS, headers=reader)).json()
    ids = [r["prompt"]["id"] for r in recs]
    assert seed["id"] not in ids  # never recommends what you already bookmarked
    assert match["id"] in ids
    match_rec = next(r for r in recs if r["prompt"]["id"] == match["id"])
    assert "Glass Login" in match_rec["reason"]


@pytest.mark.asyncio
async def test_feed_falls_back_to_trending_for_new_user(client: AsyncClient) -> None:
    _, author = await make_user(client)
    await _create(client, author, title="Popular", tags=["x"])

    _, reader = await make_user(client)  # no bookmarks yet
    recs = (await client.get(RECS, headers=reader)).json()
    assert len(recs) >= 1
    assert all(r["reason"] == "Popular right now" for r in recs)


@pytest.mark.asyncio
async def test_recommendations_require_auth(client: AsyncClient) -> None:
    assert (await client.get(RECS)).status_code == 401


@pytest.mark.asyncio
async def test_related_same_type_when_no_tags(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    source = await _create(client, headers, title="Src", prompt_type="security")
    await _create(client, headers, title="SameType", prompt_type="security")

    related = (await client.get(f"{PROMPTS}/{source['id']}/related")).json()
    assert any(p["title"] == "SameType" for p in related)
