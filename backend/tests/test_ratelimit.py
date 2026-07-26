"""Rate limiter unit tests + an end-to-end 429 on the download route."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.core import ratelimit
from app.core.config import settings
from app.core.ratelimit import InMemoryRateLimiter
from tests.conftest import make_user


def test_limiter_allows_up_to_limit_then_blocks() -> None:
    rl = InMemoryRateLimiter()
    for _ in range(3):
        allowed, _ = rl.check("k", 3, 60)
        assert allowed
    blocked, retry = rl.check("k", 3, 60)
    assert not blocked
    assert retry > 0


def test_limiter_isolates_keys_and_resets() -> None:
    rl = InMemoryRateLimiter()
    assert rl.check("a", 1, 60)[0] is True
    assert rl.check("a", 1, 60)[0] is False
    assert rl.check("b", 1, 60)[0] is True  # a different caller is unaffected
    rl.reset()
    assert rl.check("a", 1, 60)[0] is True  # cleared


@pytest.mark.asyncio
async def test_download_route_is_rate_limited(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    ratelimit._limiter.reset()
    monkeypatch.setattr(settings, "RATE_LIMIT_DOWNLOAD_PER_MIN", 1)
    try:
        _, headers = await make_user(client)
        proj = (
            await client.post("/api/v1/projects", json={"name": "Rate"}, headers=headers)
        ).json()
        url = f"/api/v1/projects/{proj['id']}/template/download"

        # First call is allowed (404 — no template — but it consumes the quota).
        first = await client.get(url)
        assert first.status_code == 404
        # Second call trips the limiter before the handler runs.
        second = await client.get(url)
        assert second.status_code == 429
        assert "Retry-After" in second.headers
    finally:
        ratelimit._limiter.reset()
