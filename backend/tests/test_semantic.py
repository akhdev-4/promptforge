"""Semantic search endpoint — without a key it must fall back to keyword search."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.conftest import make_user

PROMPTS = "/api/v1/prompts"


@pytest.mark.asyncio
async def test_semantic_falls_back_to_keyword(client: AsyncClient) -> None:
    _, headers = await make_user(client)
    await client.post(
        PROMPTS,
        json={
            "title": "Zebra Login Screen",
            "content": "x",
            "prompt_type": "ui",
            "complexity": "beginner",
            "status": "published",
        },
        headers=headers,
    )
    # No embeddings configured in tests -> keyword fallback still finds it.
    resp = await client.get(f"{PROMPTS}/semantic", params={"q": "Zebra"})
    assert resp.status_code == 200, resp.text
    assert any(p["title"] == "Zebra Login Screen" for p in resp.json())


@pytest.mark.asyncio
async def test_backfill_requires_admin(client: AsyncClient) -> None:
    _, headers = await make_user(client)  # contributor
    assert (await client.post(f"{PROMPTS}/embeddings/backfill", headers=headers)).status_code == 403
    assert (await client.post(f"{PROMPTS}/embeddings/backfill")).status_code == 401
