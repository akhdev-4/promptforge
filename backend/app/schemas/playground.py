"""Playground (prompt runner) schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class PlaygroundRunRequest(BaseModel):
    variables: dict[str, str] = Field(default_factory=dict)


class PlaygroundRunResult(BaseModel):
    output: str
    rendered_prompt: str
    provider: str
    model: str | None = None
    is_demo: bool
