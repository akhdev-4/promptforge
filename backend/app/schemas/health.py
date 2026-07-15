"""Health-check response schema."""

from __future__ import annotations

from pydantic import BaseModel


class HealthStatus(BaseModel):
    status: str
    service: str
    version: str
    environment: str
    database: str
