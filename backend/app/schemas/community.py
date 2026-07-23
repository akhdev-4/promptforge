"""Schemas for comments, reports, notifications."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# --- Comments ---------------------------------------------------------------
class CommentAuthor(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str | None
    full_name: str | None
    avatar_url: str | None


class CommentCreate(BaseModel):
    body: str = Field(min_length=1, max_length=2000)


class CommentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    body: str
    author: CommentAuthor
    created_at: datetime


# --- Reports ----------------------------------------------------------------
class ReportCreate(BaseModel):
    reason: str = Field(min_length=1, max_length=500)


class ReportPromptRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    slug: str


class ReportReporterRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str | None


class ReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    reason: str
    status: str
    prompt: ReportPromptRef
    reporter: ReportReporterRef | None
    created_at: datetime


class ReportUpdate(BaseModel):
    status: Literal["resolved", "dismissed"]


# --- Notifications ----------------------------------------------------------
class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    type: str
    message: str
    link: str | None
    is_read: bool
    created_at: datetime


class UnreadCount(BaseModel):
    unread: int
