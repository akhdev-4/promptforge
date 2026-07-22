"""Playground (prompt runner) schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class PlaygroundRunRequest(BaseModel):
    variables: dict[str, str] = Field(default_factory=dict)
    mode: Literal["text", "image"] = "text"


class PlaygroundRunResult(BaseModel):
    output: str
    rendered_prompt: str
    provider: str
    model: str | None = None
    is_demo: bool
    image_url: str | None = None
