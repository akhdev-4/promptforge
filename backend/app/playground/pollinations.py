"""Free text-to-image provider (Pollinations) — no key, no billing.

Generates a NEW image from the prompt text. It cannot edit a user-supplied
photo (identity-preserving edits need a paid model); the UI makes that clear.
We just build the image URL (Pollinations renders on load), so there's no
server-side network call.
"""

from __future__ import annotations

import random
import re
from urllib.parse import quote

from app.playground.base import RunResult

_BASE = "https://image.pollinations.ai/prompt/"
_MAX_PROMPT = 1200  # keep the generated URL well under length limits


def _clean(prompt: str) -> str:
    """Flatten a prompt into a single URL-safe line. Slashes (even encoded as
    %2F) and newlines break Pollinations' path routing (-> 404), so drop them."""
    text = prompt.replace("/", " ")
    text = re.sub(r"\s+", " ", text)  # newlines + runs of whitespace -> one space
    return text.strip()[:_MAX_PROMPT]


class PollinationsProvider:
    async def run(self, prompt: str) -> RunResult:
        text = _clean(prompt)
        seed = random.randint(1, 10_000_000)
        url = f"{_BASE}{quote(text)}?width=768&height=768&nologo=true&seed={seed}"
        return RunResult(
            output="",
            provider="pollinations",
            model="pollinations",
            is_demo=False,
            image_url=url,
        )
