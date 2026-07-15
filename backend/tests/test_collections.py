"""Collections, likes, and bookmarks tests."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.conftest import make_user

PROMPTS = "/api/v1/prompts"
COLLECTIONS = "/api/v1/collections"


async def _prompt(client: AsyncClient, headers: dict, title: str = "P") -> dict:
    return (
        await client.post(
            PROMPTS,
            json={
                "title": title,
                "content": "...",
                "prompt_type": "ui",
                "complexity": "intermediate",
                "status": "published",
            },
            headers=headers,
        )
    ).json()


@pytest.mark.asyncio
async def test_like_toggle_updates_count(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    p = await _prompt(client, headers)

    on = (await client.post(f"{PROMPTS}/{p['id']}/like", headers=headers)).json()
    assert on == {"liked": True, "likes_count": 1}
    off = (await client.post(f"{PROMPTS}/{p['id']}/like", headers=headers)).json()
    assert off == {"liked": False, "likes_count": 0}


@pytest.mark.asyncio
async def test_bookmark_toggle_and_flags_on_detail(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    p = await _prompt(client, headers)

    res = (await client.post(f"{PROMPTS}/{p['id']}/bookmark", headers=headers)).json()
    assert res == {"bookmarked": True}

    # Detail, when authenticated, reflects the flags.
    detail = (await client.get(f"{PROMPTS}/{p['id']}", headers=headers)).json()
    assert detail["is_bookmarked"] is True
    assert detail["is_liked"] is False

    # Anonymous detail defaults flags to false.
    anon = (await client.get(f"{PROMPTS}/{p['id']}")).json()
    assert anon["is_bookmarked"] is False


@pytest.mark.asyncio
async def test_my_bookmarks_list(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    p = await _prompt(client, headers, "Bookmarked")
    await client.post(f"{PROMPTS}/{p['id']}/bookmark", headers=headers)

    resp = await client.get("/api/v1/users/me/bookmarks", headers=headers)
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "Bookmarked"


@pytest.mark.asyncio
async def test_collection_crud_and_membership(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    p1 = await _prompt(client, headers, "One")
    p2 = await _prompt(client, headers, "Two")

    coll = (
        await client.post(
            COLLECTIONS, json={"name": "Best Logins"}, headers=headers
        )
    ).json()
    assert coll["item_count"] == 0

    await client.post(
        f"{COLLECTIONS}/{coll['id']}/items", json={"prompt_id": p1["id"]}, headers=headers
    )
    added = await client.post(
        f"{COLLECTIONS}/{coll['id']}/items", json={"prompt_id": p2["id"]}, headers=headers
    )
    assert added.json()["item_count"] == 2

    detail = (await client.get(f"{COLLECTIONS}/{coll['id']}")).json()
    titles = [i["title"] for i in detail["items"]]
    assert titles == ["One", "Two"]

    # Duplicate add conflicts.
    dup = await client.post(
        f"{COLLECTIONS}/{coll['id']}/items", json={"prompt_id": p1["id"]}, headers=headers
    )
    assert dup.status_code == 409

    # Remove one.
    await client.delete(f"{COLLECTIONS}/{coll['id']}/items/{p1['id']}", headers=headers)
    detail = (await client.get(f"{COLLECTIONS}/{coll['id']}")).json()
    assert [i["title"] for i in detail["items"]] == ["Two"]


@pytest.mark.asyncio
async def test_private_collection_hidden_from_others(client: AsyncClient) -> None:
    _, owner = await make_user(client)
    _, other = await make_user(client)
    coll = (
        await client.post(
            COLLECTIONS,
            json={"name": "Secret", "is_public": False},
            headers=owner,
        )
    ).json()

    # Owner can view.
    assert (await client.get(f"{COLLECTIONS}/{coll['id']}", headers=owner)).status_code == 200
    # Another user cannot.
    assert (
        await client.get(f"{COLLECTIONS}/{coll['id']}", headers=other)
    ).status_code == 403
    # Anonymous cannot.
    assert (await client.get(f"{COLLECTIONS}/{coll['id']}")).status_code == 403

    # Private collection excluded from the public list.
    public = (await client.get(COLLECTIONS)).json()
    assert all(c["id"] != coll["id"] for c in public["items"])


@pytest.mark.asyncio
async def test_non_owner_cannot_add_to_collection(client: AsyncClient) -> None:
    _, owner = await make_user(client)
    _, other = await make_user(client)
    p = await _prompt(client, other, "X")
    coll = (
        await client.post(COLLECTIONS, json={"name": "Mine"}, headers=owner)
    ).json()
    resp = await client.post(
        f"{COLLECTIONS}/{coll['id']}/items", json={"prompt_id": p["id"]}, headers=other
    )
    assert resp.status_code == 403
