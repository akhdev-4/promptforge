"""Application hierarchy: Project → Module → Component.

A Component holds multiple prompt *variants* (e.g. a "Login" component with
Modern SaaS, Apple-style, Glass, … implementations), letting an application be
assembled from proven prompt modules.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.db.types import GUID
from app.models.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.prompt import Prompt
    from app.models.user import User


class Project(UUIDMixin, TimestampMixin, Base):
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(180), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000))
    icon: Mapped[str | None] = mapped_column(String(60))

    author_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    author: Mapped[User] = relationship(lazy="joined")

    modules: Mapped[list[Module]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="Module.position",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Project {self.slug}>"


class Module(UUIDMixin, TimestampMixin, Base):
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    slug: Mapped[str] = mapped_column(String(180), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000))
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    project_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    project: Mapped[Project] = relationship(back_populates="modules")

    components: Mapped[list[Component]] = relationship(
        back_populates="module",
        cascade="all, delete-orphan",
        order_by="Component.position",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Module {self.slug}>"


class Component(UUIDMixin, TimestampMixin, Base):
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    slug: Mapped[str] = mapped_column(String(180), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000))
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    module_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("modules.id", ondelete="CASCADE"), nullable=False, index=True
    )
    module: Mapped[Module] = relationship(back_populates="components")

    prompts: Mapped[list[Prompt]] = relationship(back_populates="component")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Component {self.slug}>"
