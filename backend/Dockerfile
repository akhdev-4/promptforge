FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install dependencies first for better layer caching.
COPY pyproject.toml ./
RUN pip install --upgrade pip && pip install ".[dev]"

COPY . .

EXPOSE 8000

# Uses the module path so it works regardless of working dir.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
