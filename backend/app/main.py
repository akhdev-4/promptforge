"""Application factory and ASGI entrypoint.

Run locally with:  uvicorn app.main:app --reload
"""

from __future__ import annotations

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app import __version__
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging, get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown hooks."""
    configure_logging()
    logger.info("Starting %s (%s) — env=%s", settings.PROJECT_NAME, __version__, settings.ENVIRONMENT)

    if settings.AUTO_CREATE_TABLES:
        # Convenience for SQLite/local dev. Production uses Alembic migrations.
        from app.db.base import Base
        from app.db.session import engine

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Ensured database tables exist (AUTO_CREATE_TABLES=on)")

    yield

    from app.db.session import engine

    await engine.dispose()
    logger.info("Shutdown complete")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=__version__,
        description="Production-tested AI prompt knowledge platform.",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(o) for o in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Compress large JSON payloads (prompt bodies, lists) over the wire.
    app.add_middleware(GZipMiddleware, minimum_size=1024)

    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        response.headers["X-Process-Time-ms"] = f"{(time.perf_counter() - start) * 1000:.1f}"
        return response

    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    @app.get("/", include_in_schema=False)
    async def root() -> dict[str, str]:
        return {"service": settings.PROJECT_NAME, "docs": "/docs", "version": __version__}

    return app


app = create_app()
