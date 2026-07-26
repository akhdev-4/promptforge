"""Lightweight in-memory rate limiting.

A sliding-window request log keyed per caller (API key or client IP). It's
process-local — fine for a single-instance deployment; if the app is ever scaled
horizontally, back this with Redis behind the same ``check`` interface.

Dependencies read their limit from ``settings`` at request time (not import
time) so tests can lower a limit via monkeypatch.
"""

from __future__ import annotations

import time
from collections import defaultdict

from fastapi import HTTPException, Request, status

from app.core.config import settings


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._hits: dict[str, list[float]] = defaultdict(list)

    def check(self, key: str, limit: int, window: float) -> tuple[bool, float]:
        """Record a hit for ``key``. Returns ``(allowed, retry_after_seconds)``."""
        now = time.monotonic()
        cutoff = now - window
        bucket = self._hits[key]
        # Drop timestamps that have aged out of the window.
        i = 0
        while i < len(bucket) and bucket[i] < cutoff:
            i += 1
        if i:
            del bucket[:i]
        if len(bucket) >= limit:
            return False, window - (now - bucket[0])
        bucket.append(now)
        if not bucket:  # pragma: no cover - defensive
            self._hits.pop(key, None)
        return True, 0.0

    def reset(self) -> None:
        self._hits.clear()


_limiter = InMemoryRateLimiter()


def _identify(request: Request, by: str) -> str:
    if by == "key":
        header = request.headers.get("x-api-key")
        if header:
            return header
    client = request.client
    return client.host if client else "anonymous"


def rate_limit(scope: str, limit_attr: str, *, by: str = "ip", window: float = 60.0):
    """Build a dependency that enforces ``settings.<limit_attr>`` per ``window``.

    ``scope`` namespaces the bucket so different endpoints don't share a counter.
    ``by`` is ``"key"`` (X-API-Key header) or ``"ip"`` (client address).
    """

    async def _dependency(request: Request) -> None:
        if not settings.RATE_LIMIT_ENABLED:
            return
        limit = int(getattr(settings, limit_attr))
        if limit <= 0:
            return
        allowed, retry_after = _limiter.check(
            f"{scope}:{_identify(request, by)}", limit, window
        )
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please slow down.",
                headers={"Retry-After": str(int(retry_after) + 1)},
            )

    return _dependency
