# Deploying PromptForge

PromptForge is full-stack, so a cloud deploy has three parts:

| Piece | Host | Notes |
|-------|------|-------|
| FastAPI backend | **FastAPI Cloud** (`fastapi deploy`) | this guide |
| PostgreSQL | **Neon** | 1-click integration in FastAPI Cloud, or bring your own URL |
| Next.js frontend | **Vercel** | separate deploy (FastAPI Cloud runs Python, not Node) |

Redis is **not required** at runtime today (it's Celery-ready only), so you can skip it.

---

## 1. Backend → FastAPI Cloud

```bash
pip install fastapi-cloud-cli        # adds the `fastapi deploy` / `fastapi cloud …` commands
cd backend
fastapi deploy                       # opens the browser to log in on first run;
                                     # pick a team → create a new app
```

`fastapi deploy` packages the `backend/` folder (respecting `.gitignore` /
`.fastapicloudignore`) and returns your app URL, e.g. `https://<app>.fastapicloud.app`.

### Database (Neon)
- Easiest: in the FastAPI Cloud dashboard, add the **Neon** integration — it
  provisions Postgres and injects `DATABASE_URL` automatically.
- Or create a Neon project yourself and copy its connection string.

> The app normalizes managed URLs automatically: `postgres://…?sslmode=require`
> becomes `postgresql+asyncpg://…` with TLS applied. No manual editing needed.

### Environment variables
```bash
fastapi cloud env set --secret SECRET_KEY "$(openssl rand -hex 32)"
fastapi cloud env set AUTO_CREATE_TABLES true      # create tables on first boot
fastapi cloud env set ENVIRONMENT production
fastapi cloud env set DEBUG false
fastapi cloud env set BACKEND_CORS_ORIGINS "https://<your-frontend>.vercel.app"
# DATABASE_URL: set by the Neon integration, or set it yourself (mark --secret)
```
Then redeploy so the new config is live: `fastapi deploy`.

Check it: open `https://<app>.fastapicloud.app/docs`.

---

## 2. Frontend → Vercel

1. Import the GitHub repo in Vercel; set **Root Directory = `frontend`**.
2. Add env var **`NEXT_PUBLIC_API_URL = https://<app>.fastapicloud.app`**
   (baked in at build time).
3. Deploy → you get `https://<your-frontend>.vercel.app`.
4. Put that origin into the backend's `BACKEND_CORS_ORIGINS` (step 1) and redeploy
   the backend.

---

## 3. Seed the demo library (optional)

The seeders talk to the API over HTTP, so run them locally against the live URL:

```bash
cd backend
python scripts/seed_demo.py https://<app>.fastapicloud.app
```

Categories need an admin. Promote the demo user via a Neon SQL console, then seed:
```sql
UPDATE users SET role='ADMINISTRATOR' WHERE email='demo@promptforge.io';
```
```bash
python scripts/seed_categories.py https://<app>.fastapicloud.app
```

---

## Production migrations (instead of AUTO_CREATE_TABLES)

For a stricter setup, leave `AUTO_CREATE_TABLES=false` and run migrations against
the managed DB from your machine:

```bash
cd backend
DATABASE_URL="postgresql://…neon…?sslmode=require" alembic upgrade head
```
(The Alembic env applies TLS automatically when `sslmode=require` is present.)
