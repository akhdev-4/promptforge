# PromptForge — orientation for a new session

"GitHub for AI prompts": browse, version, run and reuse production-tested prompts,
organised as **Application → Module → Component**, plus **Starter Kits** (whole
codebases) and a public API consumed by a CLI, a VS Code extension and a browser
extension.

This file is context for anyone (human or agent) picking the project up. It records
the decisions and traps that aren't obvious from reading the code.

---

## Layout

| Path | What |
|---|---|
| `backend/` | FastAPI + async SQLAlchemy 2.0 + Pydantic v2. Layered `api → services → repositories → models` |
| `frontend/` | Next.js 16 (App Router) + React 19 + Tailwind v4 + TanStack Query + Zustand |
| `cli/` | `promptforge` CLI (typer) over the public API |
| `vscode-extension/` | VS Code extension (`DevAk.promptforge-kits`) |
| `browser-extension/` | Chromium MV3 extension — capture prompts from any AI chat |
| `deploy/`, `docker-compose.yml`, `Makefile` | Self-hosting |

The three client apps are **thin consumers of `/api/v1/public/*`** — they need no
backend changes to evolve.

---

## Running locally

```bash
# Backend — note the venv already exists; always use its interpreter
cd backend && ./.venv/Scripts/python.exe -m uvicorn app.main:app --reload   # :8000
cd frontend && npm run dev                                                  # :3000
```

Backend falls back to a local SQLite file when `DATABASE_URL` is unset, so it runs
with zero external services.

```bash
# Checks (run these before committing)
cd backend && ./.venv/Scripts/python.exe -m pytest -q          # ~119 tests
cd backend && ./.venv/Scripts/python.exe -m ruff check app/ tests/
cd frontend && npx tsc --noEmit && npm run build
```

`backend/scripts/` is **not** in the lint scope and has pre-existing E501s — ignore them.

---

## Deploying

Two supported shapes:

1. **Managed (current production):** backend on FastAPI Cloud, Postgres on Neon,
   frontend on Vercel. See `DEPLOY_FASTAPI_CLOUD.md`.
2. **Self-hosted (org server):** `docker compose up -d` brings up Postgres, the
   backend, the frontend and nginx. `redis` is in the compose file but **nothing
   imports it** — the app has no queue or worker; it's leftover scaffolding.

### Environment that actually matters

| Var | Why it bites |
|---|---|
| `DATABASE_URL` | Postgres URL; `postgres://` and `?sslmode=` are normalised for asyncpg automatically |
| `SECRET_KEY` | JWT signing — must be set in production |
| `BACKEND_CORS_ORIGINS` | Comma-separated; the frontend origin must be listed or every request fails |
| `FRONTEND_URL` | Used to build **emailed links** (verification, reset, team invites). If unset they point at `localhost:3000` |
| `SMTP_*` | Optional. Unset ⇒ email silently no-ops and features fall back to copyable links |
| `GEMINI_API_KEY` + `LLM_PROVIDER=gemini` | Optional; without it the Playground serves mock output |
| `AUTO_CREATE_TABLES` | See the migrations trap below |
| `NEXT_PUBLIC_API_URL` | Frontend → backend base URL, no trailing slash |

---

## Traps that have already cost time

**Migrations.** `AUTO_CREATE_TABLES=true` runs `create_all` on boot, which creates
**new tables but never adds columns to existing ones**. That silently broke
production twice. Alembic history was ~8 features stale and was caught up in one
revision; `alembic check` now reports no drift and a DB rebuilds from zero. On an
existing database run `alembic stamp head` **before** `alembic upgrade head`, then
set `AUTO_CREATE_TABLES=false` and let migrations own the schema. Any `NOT NULL`
column added to a populated table needs a `server_default`.

**Python is 3.10.** No `datetime.UTC` (`timezone.utc` only) and no `StrEnum`. Ruff is
pinned to `target-version = py310`; running `ruff --fix` under a newer target rewrites
code that then breaks.

**SQLite vs Postgres datetimes.** SQLite hands back **naive** datetimes, Postgres
aware ones. Comparing a stored `expires_at` to `datetime.now(timezone.utc)` raises in
tests unless you normalise first — see `TeamService._is_expired`.

**Enums aren't enforced by the DB.** `prompt_type` etc. are `Enum(native_enum=False)`,
which renders as plain `VARCHAR` with **no CHECK constraint**. Adding an enum value is
a Python-only change — no migration.

**Passwords use `bcrypt` directly**, not passlib: passlib couples to bcrypt internals
and broke in production when the deployed bcrypt version drifted.

**Gemini model names.** `gemini-flash-latest` for text and `gemini-embedding-001` for
embeddings. `text-embedding-004` 404s; image editing needs billing.

**FastAPI Cloud times out around 20s.** Long generations must stream
(`StreamingResponse` + SSE) or the gateway 502s a buffered response.

**Next.js 16 is not the Next you remember** — `params`/`searchParams` are Promises,
`middleware` became `proxy` (auth is guarded client-side in `AppShell`). See
`frontend/AGENTS.md`; consult `node_modules/next/dist/docs/` before writing Next code.

**Client-side auth.** `apiFetch` attaches the token unless `auth: false`. Endpoints
using `OptionalUser` (notably `GET /prompts`) **must not** pass `auth: false`, or
per-user behaviour like "My drafts" silently 401s.

---

## Domain rules worth knowing

- **Visibility.** Drafts are private to their author (moderators excepted); anonymous
  requests for non-published prompts are rejected. Prompts private to a team are
  hidden everywhere — list, search, semantic, related, public API — and return **404**
  rather than 403, so their existence isn't leaked. Privacy is via a `PromptTeam` join
  table, deliberately avoiding a column on `prompts`.
- **Versioning.** Metadata edits mutate the prompt in place; **only new content
  creates a version**. Each version records its own author, so history shows
  "created by" vs "edited by".
- **Fork vs contribute.** Forking copies a prompt into a new **draft** you own.
  Alternatively the owner can tick `allow_contributions`, letting any signed-in user
  add versions to the original; team members can always co-author team prompts.
  Deleting and metadata edits stay with the owner.
- **API keys** are stored as a SHA-256 digest with a display prefix — the secret is
  shown once. Keys are **read-only by default**; publishing needs an explicit write
  scope.
- **Starter Kits** are Projects with a `ProjectTemplate` (a Git repo URL). The
  codebase zip is **streamed through the API** so the source repo stays an
  implementation detail and always serves latest. The repo must be **public** —
  GitHub 404s private repos to anonymous fetches.
- **Rate limiting** is in-memory **per process**. It will not hold across multiple
  instances; back it with Redis before scaling horizontally.

---

## State

All 11 original milestones plus: Playground (Gemini/Pollinations), community
(comments, reports, moderation, notifications), teams with email invites, semantic
search, onboarding tour, API keys + public API, Starter Kits with previews, kit
download counts, email verification and password reset, and the three client apps.

Known gaps, roughly by value: **no error tracking** (production failures are
invisible), **no frontend tests** (backend has ~119), keyword search is a naive
`LIKE %whole phrase%` so multi-word queries miss, and prompt pages are **entirely
behind the login wall** — there is no public/shareable view, which blocks any
organic growth. `User.oauth_provider`/`oauth_subject` exist but are unused
scaffolding if OAuth login is ever wanted.
