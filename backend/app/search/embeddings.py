"""Gemini text-embedding provider (free tier). Best-effort: returns None on any
failure or when no key is configured, so callers can fall back to keyword search."""

from __future__ import annotations

import httpx

from app.core.config import settings

_MODEL = "text-embedding-004"
_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{_MODEL}:embedContent"

EMBED_MODEL = _MODEL


def embeddings_enabled() -> bool:
    return settings.LLM_PROVIDER == "gemini" and bool(settings.GEMINI_API_KEY)


async def embed_text(text: str) -> list[float] | None:
    if not embeddings_enabled():
        return None
    body = {"model": f"models/{_MODEL}", "content": {"parts": [{"text": text[:2000]}]}}
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                _ENDPOINT, headers={"x-goog-api-key": settings.GEMINI_API_KEY}, json=body
            )
        if resp.status_code != 200:
            return None
        return resp.json()["embedding"]["values"]
    except (httpx.HTTPError, KeyError, ValueError):
        return None
