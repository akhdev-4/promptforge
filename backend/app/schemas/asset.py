"""Prompt asset and version-compare schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.asset import AssetKind

_URL_KINDS = {AssetKind.SCREENSHOT, AssetKind.IMAGE, AssetKind.VIDEO, AssetKind.LIVE_DEMO}
_CONTENT_KINDS = {AssetKind.GENERATED_HTML, AssetKind.GENERATED_CODE}


class AssetCreate(BaseModel):
    kind: AssetKind
    # No length cap — may hold a compressed inline data: URL (uploaded image).
    url: str | None = None
    content: str | None = None
    language: str | None = Field(default=None, max_length=40)
    caption: str | None = Field(default=None, max_length=300)
    position: int = 0

    @model_validator(mode="after")
    def _check_payload(self) -> AssetCreate:
        if self.kind in _URL_KINDS and not self.url:
            raise ValueError(f"{self.kind.value} requires a 'url'")
        if self.kind in _CONTENT_KINDS and not self.content:
            raise ValueError(f"{self.kind.value} requires 'content'")
        return self


class AssetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    kind: AssetKind
    url: str | None
    content: str | None
    language: str | None
    caption: str | None
    position: int
    created_at: datetime


# --- Version comparison -----------------------------------------------------
class VersionSide(BaseModel):
    version_number: int
    title: str
    content: str
    change_summary: str | None


class DiffLine(BaseModel):
    op: str  # "equal" | "insert" | "delete"
    text: str


class VersionCompare(BaseModel):
    from_version: VersionSide
    to_version: VersionSide
    diff: list[DiffLine]
    added: int
    removed: int
