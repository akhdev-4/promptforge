"""Zero-key demo provider: returns a clearly-labeled placeholder, never a
fabricated 'real' answer."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

from app.playground.base import RunResult


def _demo_text(prompt: str) -> str:
    preview = prompt.strip()
    if len(preview) > 500:
        preview = preview[:500] + "…"
    return (
        "🧪 Demo mode — no AI model is connected yet.\n\n"
        "To see the real output this prompt produces, set a free Gemini key "
        "(GEMINI_API_KEY from aistudio.google.com) and LLM_PROVIDER=gemini on "
        "the backend. Nothing else changes.\n\n"
        "——— Prompt that would be sent ———\n"
        f"{preview}"
    )


class MockProvider:
    async def run(self, prompt: str) -> RunResult:
        return RunResult(output=_demo_text(prompt), provider="demo", model=None, is_demo=True)

    async def stream(self, prompt: str) -> AsyncIterator[str]:
        for word in _demo_text(prompt).split(" "):
            yield word + " "
            await asyncio.sleep(0.02)
