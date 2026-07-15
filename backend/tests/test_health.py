"""Smoke tests for the health endpoints and app wiring."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root(client: AsyncClient) -> None:
    resp = await client.get("/")
    assert resp.status_code == 200
    assert resp.json()["service"] == "PromptForge"


@pytest.mark.asyncio
async def test_health_liveness(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["database"] == "sqlite"


@pytest.mark.asyncio
async def test_health_readiness(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/health/ready")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ready"


@pytest.mark.asyncio
async def test_openapi_schema(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/openapi.json")
    assert resp.status_code == 200
    assert resp.json()["info"]["title"] == "PromptForge"
