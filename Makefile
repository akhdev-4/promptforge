# PromptForge developer shortcuts.
.PHONY: help backend frontend test lint typecheck build up down migrate

help:
	@echo "PromptForge commands:"
	@echo "  make backend    - run FastAPI dev server (SQLite)"
	@echo "  make frontend   - run Next.js dev server"
	@echo "  make test       - backend tests"
	@echo "  make lint       - backend ruff + frontend tsc"
	@echo "  make build      - frontend production build"
	@echo "  make up / down  - full docker compose stack"
	@echo "  make migrate    - apply DB migrations"

backend:
	cd backend && uvicorn app.main:app --reload

frontend:
	cd frontend && npm run dev

test:
	cd backend && pytest -q

lint:
	cd backend && ruff check .
	cd frontend && npx tsc --noEmit

typecheck:
	cd frontend && npx tsc --noEmit

build:
	cd frontend && npm run build

migrate:
	cd backend && alembic upgrade head

up:
	docker compose up --build

down:
	docker compose down
