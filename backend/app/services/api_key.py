"""API key lifecycle + authentication for the public API."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.models.api_key import ApiKey
from app.models.user import User
from app.repositories.base import BaseRepository

# A user can hold at most this many live keys — a small guard against runaway
# key creation, not a paid-plan limit.
MAX_KEYS_PER_USER = 20


class ApiKeyService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.keys = BaseRepository(ApiKey, session)

    async def create(
        self, user: User, name: str, *, write: bool = False
    ) -> tuple[ApiKey, str]:
        """Mint a key. Returns the row plus the one-time plaintext secret.

        ``write=True`` grants publish access ("read write"); otherwise the key is
        read-only ("read").
        """
        live = await self.keys.count(user_id=user.id, revoked_at=None)
        if live >= MAX_KEYS_PER_USER:
            raise PermissionDeniedError(
                f"You can have at most {MAX_KEYS_PER_USER} active keys; revoke one first."
            )
        full_key, prefix, hashed = security.generate_api_key()
        key = await self.keys.create(
            user_id=user.id,
            name=name,
            prefix=prefix,
            hashed_key=hashed,
            scopes="read write" if write else "read",
        )
        return key, full_key

    async def list_for_user(self, user: User) -> list[ApiKey]:
        stmt = (
            select(ApiKey)
            .where(ApiKey.user_id == user.id)
            .order_by(ApiKey.created_at.desc())
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def revoke(self, user: User, key_id: uuid.UUID) -> None:
        key = await self.keys.get(key_id)
        if key is None or key.user_id != user.id:
            raise NotFoundError("API key not found")
        if key.revoked_at is None:
            key.revoked_at = datetime.now(timezone.utc)
            self.session.add(key)
            await self.session.flush()

    async def resolve(self, presented: str) -> ApiKey | None:
        """Return the active ApiKey for a presented secret (touches last_used)."""
        if not presented or not presented.startswith(security.API_KEY_PREFIX):
            return None
        hashed = security.hash_api_key(presented)
        key = await self.keys.get_by(hashed_key=hashed)
        if key is None or key.revoked_at is not None:
            return None
        key.last_used_at = datetime.now(timezone.utc)
        self.session.add(key)
        await self.session.flush()
        return key

    async def authenticate(self, presented: str) -> User | None:
        """Resolve the owning user for a presented key, or ``None``."""
        key = await self.resolve(presented)
        if key is None:
            return None
        user = await self.session.get(User, key.user_id)
        return user if user and user.is_active else None

    @staticmethod
    def has_scope(key: ApiKey, scope: str) -> bool:
        return scope in (key.scopes or "").split()
