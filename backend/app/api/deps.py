"""Shared FastAPI dependencies: DB session, current user, role guards."""

from __future__ import annotations

import uuid
from collections.abc import Callable, Coroutine
from typing import Annotated, Any

from fastapi import Depends
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.config import settings
from app.core.exceptions import AuthenticationError, PermissionDeniedError
from app.db.session import get_db
from app.models.user import User, UserRole
from app.repositories.user import UserRepository
from app.services.api_key import ApiKeyService

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login",
    auto_error=False,
)

# Public-API authentication: clients send their key in the ``X-API-Key`` header.
api_key_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)

DbSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    db: DbSession,
    token: Annotated[str | None, Depends(oauth2_scheme)],
) -> User:
    if not token:
        raise AuthenticationError("Not authenticated")
    try:
        payload = security.decode_token(token, expected_type="access")
    except ValueError as exc:
        raise AuthenticationError(str(exc)) from exc

    sub = payload.get("sub")
    try:
        user_id = uuid.UUID(str(sub))
    except (ValueError, TypeError) as exc:
        raise AuthenticationError("Invalid token subject") from exc

    user = await UserRepository(db).get(user_id)
    if user is None or not user.is_active:
        raise AuthenticationError("User not found or inactive")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_optional_user(
    db: DbSession,
    token: Annotated[str | None, Depends(oauth2_scheme)],
) -> User | None:
    """Resolve the user if a valid token is present; otherwise ``None``.

    Used by public endpoints that enrich responses for signed-in users
    (e.g. is_liked/is_bookmarked flags) without requiring auth.
    """
    if not token:
        return None
    try:
        payload = security.decode_token(token, expected_type="access")
        user_id = uuid.UUID(str(payload.get("sub")))
    except (ValueError, TypeError):
        return None
    user = await UserRepository(db).get(user_id)
    return user if user and user.is_active else None


OptionalUser = Annotated[User | None, Depends(get_optional_user)]


async def get_api_key_user(
    db: DbSession,
    key: Annotated[str | None, Depends(api_key_scheme)],
) -> User:
    """Authenticate a public-API request via its ``X-API-Key`` header."""
    if not key:
        raise AuthenticationError("Provide your API key in the X-API-Key header")
    user = await ApiKeyService(db).authenticate(key)
    if user is None:
        raise AuthenticationError("Invalid or revoked API key")
    return user


ApiKeyUser = Annotated[User, Depends(get_api_key_user)]


async def get_write_api_key_user(
    db: DbSession,
    key: Annotated[str | None, Depends(api_key_scheme)],
) -> User:
    """Authenticate a public-API request that needs *write* scope (publishing)."""
    if not key:
        raise AuthenticationError("Provide your API key in the X-API-Key header")
    service = ApiKeyService(db)
    api_key = await service.resolve(key)
    if api_key is None:
        raise AuthenticationError("Invalid or revoked API key")
    user = await UserRepository(db).get(api_key.user_id)
    if user is None or not user.is_active:
        raise AuthenticationError("User not found or inactive")
    if not service.has_scope(api_key, "write"):
        raise PermissionDeniedError(
            "This API key is read-only. Create a write-enabled key to publish."
        )
    return user


WriteApiKeyUser = Annotated[User, Depends(get_write_api_key_user)]


async def get_current_active_verified_user(user: CurrentUser) -> User:
    if not user.is_verified:
        raise PermissionDeniedError("Email verification required")
    return user


def require_role(
    minimum: UserRole,
) -> Callable[[User], Coroutine[Any, Any, User]]:
    """Guard factory: require at least ``minimum`` privilege level."""

    async def _guard(user: CurrentUser) -> User:
        if not user.role.satisfies(minimum):
            raise PermissionDeniedError(
                f"Requires {minimum.value} role or higher"
            )
        return user

    return _guard


require_contributor = require_role(UserRole.CONTRIBUTOR)
require_moderator = require_role(UserRole.MODERATOR)
require_admin = require_role(UserRole.ADMINISTRATOR)
