"""User request/response schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    username: str | None = Field(default=None, min_length=3, max_length=50)
    full_name: str | None = Field(default=None, max_length=120)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=50)
    full_name: str | None = Field(default=None, max_length=120)
    bio: str | None = Field(default=None, max_length=500)
    avatar_url: str | None = Field(default=None, max_length=500)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    username: str | None
    full_name: str | None
    role: UserRole
    is_active: bool
    is_verified: bool
    avatar_url: str | None
    bio: str | None
    created_at: datetime


class UserPublic(BaseModel):
    """Trimmed view safe to expose on public profile pages."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str | None
    full_name: str | None
    avatar_url: str | None
    bio: str | None
    role: UserRole
    created_at: datetime
