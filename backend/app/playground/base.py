"""Playground run-provider protocol + prompt templating helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol

# Matches {{ variable }} placeholders (word chars, dot, hyphen; optional spaces).
_VAR_RE = re.compile(r"\{\{\s*([\w.\-]+)\s*\}\}")


def extract_variables(content: str) -> list[str]:
    """Ordered, de-duplicated list of {{variable}} names found in a prompt."""
    out: list[str] = []
    seen: set[str] = set()
    for m in _VAR_RE.finditer(content):
        name = m.group(1)
        if name not in seen:
            seen.add(name)
            out.append(name)
    return out


def render_prompt(content: str, variables: dict[str, str]) -> str:
    """Substitute provided variables; leave unknown placeholders untouched."""
    return _VAR_RE.sub(lambda m: variables.get(m.group(1), m.group(0)), content)


@dataclass
class RunResult:
    output: str
    provider: str
    model: str | None
    is_demo: bool
    image_url: str | None = None


class RunProvider(Protocol):
    """Anything that can turn a rendered prompt into model output."""

    async def run(self, prompt: str) -> RunResult: ...
