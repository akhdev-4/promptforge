# PromptForge

> The GitHub + Figma Community + Notion for AI prompts — a production-tested
> prompt knowledge platform where every completed AI conversation becomes a
> reusable engineering asset.

PromptForge lets developers browse, preview, compare, version, and instantly
reuse production-tested prompts organized into applications → modules →
components, instead of rediscovering the same solutions from scratch.

## Monorepo layout

```
promptforge/
├── backend/          FastAPI service (Python 3.11+, SQLAlchemy 2.0, async)
├── frontend/         Next.js app (App Router, TypeScript, Tailwind, shadcn/ui)  ← added in M3
├── docker-compose.yml  Postgres + Redis + backend
└── README.md
```

## Tech stack

| Layer | Choice |
|-------|--------|
| Backend | FastAPI, SQLAlchemy 2.0 (async), Pydantic v2, Alembic |
| Database | SQLite (dev) → PostgreSQL (prod) via one env var |
| Cache/Queue | Redis (Celery added later) |
| Auth | JWT (access + refresh), OAuth-ready (Google, GitHub) |
| Frontend | Next.js, TypeScript, Tailwind, shadcn/ui, TanStack Query |
| Search | PostgreSQL full-text (pluggable → Meilisearch/Elasticsearch) |
| Infra | Docker, Docker Compose, GitHub Actions |

## Build roadmap

- [x] **M1** — Project architecture & folder structure
- [x] **M2** — Authentication & user management (JWT, roles, OAuth-ready)
- [x] **M3** — Dashboard layout & navigation (Next.js shell, theming, auth UI)
- [x] **M4** — Prompt CRUD with version history (Git-style versions, fork, copy, search)
- [x] **M5** — Categories (nested tree), tags (M2M) & faceted search (swappable layer)
- [x] **M6** — Prompt detail previews (assets, live/code preview, markdown, version diff)
- [x] **M7** — Project → Module → Component hierarchy (prompt variants, tree explorer)
- [x] **M8** — Collections, favorites (like/bookmark) & sharing (public collection pages)
- [x] **M9** — Analytics dashboards (overview, trending, contributors, growth + type charts)
- [x] **M10** — AI recommendation foundations (pluggable related-prompts provider)
- [x] **M11** — Performance (gzip, timing), testing (CI), deployment (Docker, nginx, Actions)

**All 11 milestones complete.** Backend: 53 passing tests, ruff-clean. Frontend:
typecheck + production build green (14 routes).

## Getting started

Run the two apps in separate terminals.

**Backend** (zero-setup SQLite) — see [backend/README.md](backend/README.md):

```bash
cd backend
python -m venv .venv && source .venv/Scripts/activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn app.main:app --reload
# → http://localhost:8000/docs
```

**Frontend** (Next.js) — see [frontend/README.md](frontend/README.md):

```bash
cd frontend
npm install
cp .env.example .env.local   # points at http://localhost:8000
npm run dev
# → http://localhost:3000  (register → land on the dashboard)
```

## Production (Docker)

The full stack (Postgres + Redis + FastAPI + Next.js + nginx) runs behind a
single nginx entrypoint that routes `/api` → backend and everything else →
frontend:

```bash
export SECRET_KEY=$(openssl rand -hex 32)
docker compose up --build
# → http://localhost         (app)
# → http://localhost/docs    (API docs)
```

Backend migrations run automatically on startup (`alembic upgrade head`).

## CI

`.github/workflows/ci.yml` runs on every push/PR:
- **Backend** — `ruff check` + `pytest`
- **Frontend** — `tsc --noEmit` + `next build`

## Quality gates (current)

| Gate | Status |
|------|--------|
| Backend tests | **53 passing** |
| Backend lint (ruff) | **clean** |
| Frontend typecheck | **clean** |
| Frontend build | **14 routes, green** |
