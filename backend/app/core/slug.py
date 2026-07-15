"""Slug generation helpers."""

from __future__ import annotations

import re
import secrets

_slug_strip = re.compile(r"[^a-z0-9]+")


def slugify(value: str) -> str:
    slug = _slug_strip.sub("-", value.lower()).strip("-")
    return slug or "prompt"


def slug_with_suffix(value: str, length: int = 6) -> str:
    """Slug plus a short random suffix to make collisions vanishingly rare."""
    return f"{slugify(value)[:60]}-{secrets.token_hex(length // 2)}"
