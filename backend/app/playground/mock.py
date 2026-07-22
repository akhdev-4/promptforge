"""Zero-key demo provider: returns a clearly-labeled placeholder, never a
fabricated 'real' answer."""

from __future__ import annotations

from app.playground.base import RunResult


class MockProvider:
    async def run(self, prompt: str) -> RunResult:
        preview = prompt.strip()
        if len(preview) > 500:
            preview = preview[:500] + "…"
        output = (
            "🧪 Demo mode — no AI model is connected yet.\n\n"
            "To see the real output this prompt produces, set a free Gemini key "
            "(GEMINI_API_KEY from aistudio.google.com) and LLM_PROVIDER=gemini on "
            "the backend. Nothing else changes.\n\n"
            "——— Prompt that would be sent ———\n"
            f"{preview}"
        )
        return RunResult(output=output, provider="demo", model=None, is_demo=True)
