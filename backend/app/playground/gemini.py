"""Real provider: Google Gemini (free tier via Google AI Studio).

Calls the Generative Language REST API directly with httpx (no extra SDK), so
it stays lean and deploys without new heavy dependencies.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator

import httpx

from app.core.config import settings
from app.playground.base import RunResult

_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
_STREAM_ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent"
)


class GeminiProvider:
    async def run(self, prompt: str) -> RunResult:
        url = _ENDPOINT.format(model=settings.GEMINI_MODEL)
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": settings.PLAYGROUND_MAX_TOKENS},
        }
        async with httpx.AsyncClient(timeout=60) as client:
            # Key goes in a header (not the URL) so it never lands in logs/proxies.
            resp = await client.post(
                url, headers={"x-goog-api-key": settings.GEMINI_API_KEY}, json=payload
            )

        if resp.status_code != 200:
            raise RuntimeError(f"Gemini API error {resp.status_code}: {resp.text[:300]}")

        data = resp.json()
        try:
            text = data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError):
            # Safety block, empty candidate, or an unexpected shape.
            text = "(The model returned no text — it may have been blocked by safety filters.)"

        return RunResult(
            output=text, provider="gemini", model=settings.GEMINI_MODEL, is_demo=False
        )

    async def stream(self, prompt: str) -> AsyncIterator[str]:
        """Yield text deltas as Gemini generates them (SSE)."""
        url = _STREAM_ENDPOINT.format(model=settings.GEMINI_MODEL)
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": settings.PLAYGROUND_STREAM_MAX_TOKENS},
        }
        async with (
            httpx.AsyncClient(timeout=120) as client,
            client.stream(
                "POST",
                url,
                params={"alt": "sse"},
                headers={"x-goog-api-key": settings.GEMINI_API_KEY},
                json=payload,
            ) as resp,
        ):
            if resp.status_code != 200:
                body = (await resp.aread()).decode("utf-8", "replace")[:200]
                raise RuntimeError(f"Gemini stream error {resp.status_code}: {body}")
            async for line in resp.aiter_lines():
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if not data:
                    continue
                try:
                    obj = json.loads(data)
                    text = obj["candidates"][0]["content"]["parts"][0]["text"]
                except (KeyError, IndexError, TypeError, json.JSONDecodeError):
                    continue
                if text:
                    yield text
