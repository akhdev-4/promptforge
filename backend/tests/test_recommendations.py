"""Related-prompt recommendation tests."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.conftest import make_user

PROMPTS = "/api/v1/prompts"


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
async def test_related_same_type_when_no_tags(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    source = await _create(client, headers, title="Src", prompt_type="security")
    await _create(client, headers, title="SameType", prompt_type="security")

    related = (await client.get(f"{PROMPTS}/{source['id']}/related")).json()
    assert any(p["title"] == "SameType" for p in related)
