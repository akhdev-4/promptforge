"""Analytics endpoint tests."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.conftest import make_user

PROMPTS = "/api/v1/prompts"
ANALYTICS = "/api/v1/analytics"


async def _prompt(client: AsyncClient, headers: dict, **over) -> dict:
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
async def test_overview_counts(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    await _prompt(client, headers)
    await _prompt(client, headers, title="Two")

    ov = (await client.get(f"{ANALYTICS}/overview")).json()
    assert ov["total_prompts"] == 2
    assert ov["total_views"] >= 0
    assert set(ov) >= {
        "total_prompts",
        "total_categories",
        "total_collections",
        "total_projects",
        "total_tags",
        "total_copies",
        "total_likes",
    }


@pytest.mark.asyncio
async def test_trending_orders_by_copies(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    a = await _prompt(client, headers, title="Popular")
    await _prompt(client, headers, title="Quiet")
    # Copy "Popular" twice.
    await client.post(f"{PROMPTS}/{a['id']}/copy")
    await client.post(f"{PROMPTS}/{a['id']}/copy")

    trending = (await client.get(f"{ANALYTICS}/trending")).json()
    assert trending[0]["title"] == "Popular"
    assert trending[0]["copies_count"] == 2


@pytest.mark.asyncio
async def test_contributors_and_by_type(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    await _prompt(client, headers, prompt_type="ui")
    await _prompt(client, headers, prompt_type="backend", title="B")

    contributors = (await client.get(f"{ANALYTICS}/contributors")).json()
    assert contributors[0]["prompt_count"] == 2

    by_type = (await client.get(f"{ANALYTICS}/by-type")).json()
    types = {t["prompt_type"]: t["count"] for t in by_type}
    assert types.get("ui") == 1
    assert types.get("backend") == 1


@pytest.mark.asyncio
async def test_growth_is_dense_series(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    await _prompt(client, headers)

    growth = (await client.get(f"{ANALYTICS}/growth", params={"days": 7})).json()
    assert len(growth) == 7  # one point per day, gaps filled
    assert sum(p["count"] for p in growth) >= 1
    assert all("date" in p and "count" in p for p in growth)
