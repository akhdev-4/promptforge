# PromptForge — Backend

FastAPI service for the PromptForge prompt-knowledge platform.

## Architecture

Layered / clean architecture. Dependencies point inward:

```
api/         HTTP controllers (thin) — request validation, status codes
  │
services/    Business logic — orchestration, rules, no framework/ORM leakage
  │
repositories/ Data access — the only layer that touches SQLAlchemy
  │
models/      ORM entities (+ mixins)   schemas/ Pydantic contracts
  │
db/          Engine, session, Base, portable column types
core/        Config, logging, security (cross-cutting)
```

Why this shape: business logic (version diffing, search ranking, recommendations)
stays testable and framework-agnostic, satisfying the SOLID + "separate business
logic from presentation" requirements. Swapping SQLite→Postgres or PG-search→
Meilisearch touches only one layer.

## Quick start (SQLite, zero setup)

```bash
cd backend
python -m venv .venv && source .venv/Scripts/activate   # Windows Git Bash
#                     or: source .venv/bin/activate      # macOS/Linux
pip install -e ".[dev]"
cp .env.example .env
uvicorn app.main:app --reload
```

Open:
- http://localhost:8000/docs — Swagger UI
- http://localhost:8000/api/v1/health — liveness

## Run tests

```bash
pytest
```

## PostgreSQL (production-faithful)

Set `DATABASE_URL` in `.env`, then use migrations instead of auto-create:

```bash
export AUTO_CREATE_TABLES=false
alembic revision --autogenerate -m "message"
alembic upgrade head
```

Or bring up the whole stack from the repo root: `docker compose up`.

## Layout

| Path | Responsibility |
|------|----------------|
| `app/core/` | Settings (`config.py`), logging |
| `app/db/` | Async engine/session, `Base`, portable `GUID` type |
| `app/models/` | SQLAlchemy models + reusable mixins |
| `app/schemas/` | Pydantic v2 request/response models |
| `app/repositories/` | Generic + per-entity data access |
| `app/services/` | Business logic |
| `app/api/v1/` | Versioned routers and endpoints |
| `alembic/` | Database migrations |
| `tests/` | Pytest suite (in-memory SQLite) |
