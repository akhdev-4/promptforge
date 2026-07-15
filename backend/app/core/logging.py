"""Structured application logging.

A single ``configure_logging`` entrypoint is called from the app factory so log
formatting is consistent across Uvicorn workers, request handlers, and Celery
tasks (added later).
"""

from __future__ import annotations

import logging
import sys

from app.core.config import settings


def configure_logging() -> None:
    level = logging.DEBUG if settings.DEBUG else logging.INFO

    root = logging.getLogger()
    root.setLevel(level)

    # Avoid duplicate handlers when Uvicorn reloads the app.
    if root.handlers:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    )
    root.addHandler(handler)

    # Tame noisy third-party loggers.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("aiosqlite").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DB_ECHO else logging.WARNING
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
