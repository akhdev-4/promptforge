"""Declarative base with a consistent constraint-naming convention.

Explicit naming is required for Alembic autogenerate to produce stable,
reversible migrations across SQLite and PostgreSQL.
"""

from __future__ import annotations

import re

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, declared_attr

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

_CAMEL_TO_SNAKE = re.compile(r"(?<!^)(?=[A-Z])")


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)

    @declared_attr.directive
    def __tablename__(cls) -> str:  # noqa: N805
        # UserProfile -> user_profile ; append 's' for a pluralised table name.
        name = _CAMEL_TO_SNAKE.sub("_", cls.__name__).lower()
        return name if name.endswith("s") else f"{name}s"
