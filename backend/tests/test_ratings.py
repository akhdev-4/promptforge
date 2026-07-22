"""Star-rating tests."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.conftest import make_user

PROMPTS = "/api/v1/prompts"


async def _create(client: AsyncClient, headers: dict, **over) -> dict:
    payload = {
        "title": "Rate me",
        "content": "...",
        "prompt_type": "ui",
        "complexity": "intermediate",
        "status": "published",
    }
    payload.update(over)
    return (await client.post(PROMPTS, json=payload, headers=headers)).json()


@pytest.mark.asyncio
async def test_rating_aggregates_and_my_rating(client: AsyncClient) -> None:
    _, author = await make_user(client)
    prompt = await _create(client, author)

    _, a = await make_user(client)
    _, b = await make_user(client)

    r1 = await client.post(f"{PROMPTS}/{prompt['id']}/rating", json={"stars": 5}, headers=a)
    assert r1.status_code == 200, r1.text
    assert r1.json() == {"rating_avg": 5.0, "rating_count": 1, "my_rating": 5}

    r2 = await client.post(f"{PROMPTS}/{prompt['id']}/rating", json={"stars": 3}, headers=b)
    assert r2.json()["rating_count"] == 2
    assert r2.json()["rating_avg"] == 4.0  # (5 + 3) / 2

    # Detail reflects the aggregate, and my_rating is per-user.
    detail_a = (await client.get(f"{PROMPTS}/{prompt['id']}", headers=a)).json()
    assert detail_a["rating_avg"] == 4.0
    assert detail_a["rating_count"] == 2
    assert detail_a["my_rating"] == 5


@pytest.mark.asyncio
async def test_rating_is_upsert_not_duplicate(client: AsyncClient) -> None:
    _, author = await make_user(client)
    prompt = await _create(client, author)
    _, a = await make_user(client)

    await client.post(f"{PROMPTS}/{prompt['id']}/rating", json={"stars": 2}, headers=a)
    res = (
        await client.post(f"{PROMPTS}/{prompt['id']}/rating", json={"stars": 4}, headers=a)
    ).json()
    # Same user re-rating updates, not adds.
    assert res == {"rating_avg": 4.0, "rating_count": 1, "my_rating": 4}


@pytest.mark.asyncio
async def test_unrate_removes_and_recomputes(client: AsyncClient) -> None:
    _, author = await make_user(client)
    prompt = await _create(client, author)
    _, a = await make_user(client)
    _, b = await make_user(client)

    await client.post(f"{PROMPTS}/{prompt['id']}/rating", json={"stars": 5}, headers=a)
    await client.post(f"{PROMPTS}/{prompt['id']}/rating", json={"stars": 1}, headers=b)
    res = (await client.delete(f"{PROMPTS}/{prompt['id']}/rating", headers=b)).json()
    assert res == {"rating_avg": 5.0, "rating_count": 1, "my_rating": None}


@pytest.mark.asyncio
async def test_rating_bounds_enforced(client: AsyncClient) -> None:
    _, author = await make_user(client)
    prompt = await _create(client, author)
    _, a = await make_user(client)
    for bad in (0, 6, -1):
        resp = await client.post(
            f"{PROMPTS}/{prompt['id']}/rating", json={"stars": bad}, headers=a
        )
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_top_rated_sort(client: AsyncClient) -> None:
    _, author = await make_user(client)
    low = await _create(client, author, title="Low rated")
    high = await _create(client, author, title="High rated")
    _, a = await make_user(client)

    await client.post(f"{PROMPTS}/{low['id']}/rating", json={"stars": 2}, headers=a)
    await client.post(f"{PROMPTS}/{high['id']}/rating", json={"stars": 5}, headers=a)

    listed = (await client.get(PROMPTS, params={"sort": "top_rated"})).json()
    titles = [p["title"] for p in listed["items"]]
    assert titles.index("High rated") < titles.index("Low rated")


@pytest.mark.asyncio
async def test_rating_requires_auth(client: AsyncClient) -> None:
    _, author = await make_user(client)
    prompt = await _create(client, author)
    assert (
        await client.post(f"{PROMPTS}/{prompt['id']}/rating", json={"stars": 5})
    ).status_code == 401
