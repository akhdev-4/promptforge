"""Real provider: Google Gemini (free tier via Google AI Studio).

Calls the Generative Language REST API directly with httpx (no extra SDK), so
it stays lean and deploys without new heavy dependencies.
"""

from __future__ import annotations

import httpx

from app.core.config import settings
from app.playground.base import RunResult

_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


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
