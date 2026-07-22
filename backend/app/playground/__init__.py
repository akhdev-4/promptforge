"""Pluggable prompt-run providers for the Playground.

Callers depend only on ``RunProvider``. Today: a zero-key ``MockProvider``
(demo) and a real ``GeminiProvider`` that activates when a key is configured.
Swapping in OpenAI/Anthropic/image providers later needs no caller changes.
"""

from __future__ import annotations

from app.core.config import settings
from app.playground.base import (
    RunProvider,
    RunResult,
    extract_variables,
    render_prompt,
)
from app.playground.mock import MockProvider


def get_run_provider(mode: str = "text") -> RunProvider:
    if mode == "image":
        from app.playground.pollinations import PollinationsProvider

        return PollinationsProvider()
    if settings.LLM_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
        from app.playground.gemini import GeminiProvider

        return GeminiProvider()
    return MockProvider()


__all__ = [
    "RunProvider",
    "RunResult",
    "extract_variables",
    "render_prompt",
    "get_run_provider",
]
