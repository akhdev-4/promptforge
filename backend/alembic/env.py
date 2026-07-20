"""Alembic migration environment (async-aware).

Pulls the database URL and target metadata from the application so migrations
stay in lockstep with the models. Supports both online (async engine) and
offline (SQL emit) modes.
"""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from app.core.config import settings
from app.db.base import Base  # imports all models -> populates metadata

config = context.config
config.set_main_option("sqlalchemy.url", settings.sqlalchemy_database_uri)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def render_item(type_: str, obj: object, autogen_context) -> str | bool:
    """Ensure our custom ``GUID`` type renders with an import in migrations."""
    if type_ == "type" and obj.__class__.__module__.startswith("app.db.types"):
        autogen_context.imports.add("import app.db.types")
        return f"app.db.types.{obj.__class__.__name__}()"
    return False


def run_migrations_offline() -> None:
    context.configure(
        url=settings.sqlalchemy_database_uri,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        render_item=render_item,
        render_as_batch=settings.is_sqlite,  # SQLite needs batch mode for ALTER
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        render_item=render_item,
        render_as_batch=settings.is_sqlite,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connect_args = {"ssl": True} if settings.db_requires_ssl else {}
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args=connect_args,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
