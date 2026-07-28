"""Team / workspace schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class TeamCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)


class AddMember(BaseModel):
    username: str = Field(min_length=1, max_length=50)


# --- Invitations ------------------------------------------------------------
class InviteCreate(BaseModel):
    email: EmailStr


class InviteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    role: str
    status: str
    created_at: datetime
    expires_at: datetime


class InviteCreated(InviteRead):
    """Returned on creation — carries the shareable link + delivery status."""

    link: str
    email_sent: bool


class InviteInfo(BaseModel):
    """Public preview shown on the accept page."""

    team_name: str
    email: str
    status: str
    expired: bool


class TeamMemberRead(BaseModel):
    id: uuid.UUID  # the member's user id
    username: str | None
    full_name: str | None
    avatar_url: str | None
    role: str


class TeamSummary(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    description: str | None
    owner_id: uuid.UUID
    created_at: datetime
    member_count: int
    is_owner: bool


class TeamDetail(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    description: str | None
    owner_id: uuid.UUID
    created_at: datetime
    is_owner: bool
    members: list[TeamMemberRead]
