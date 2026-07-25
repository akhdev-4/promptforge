"""Starter template metadata for a Project (codebase-to-Project).

A Project with a ``ProjectTemplate`` row is a *starter template*: it points at a
real codebase (a Git repo) and carries setup hints, so the CLI / IDE plugin can
scaffold it locally and drop in the project's proven prompts. Kept in its own
table (like PromptTeam) so no existing table needs an ALTER in production.
"""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.db.types import GUID
from app.models.mixins import TimestampMixin, UUIDMixin


class ProjectTemplate(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "project_templates"
    __table_args__ = (UniqueConstraint("project_id", name="uq_project_template"),)

    project_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Curated kit type (e.g. "ecommerce"), for the Starter Kits catalog. Stored
    # as a plain string so it stays forward-compatible if the list grows.
    category: Mapped[str | None] = mapped_column(String(40), index=True)
    # Where the actual code lives — a Git URL the download endpoint archives.
    repo_url: Mapped[str] = mapped_column(String(500), nullable=False)
    # Human-readable stack summary, e.g. "Next.js + FastAPI + Stripe".
    stack: Mapped[str | None] = mapped_column(String(200))
    # One-liner to get running, e.g. "npm install && npm run dev".
    setup_command: Mapped[str | None] = mapped_column(String(300))
    # Free-form extra instructions (Markdown allowed).
    notes: Mapped[str | None] = mapped_column(Text)
