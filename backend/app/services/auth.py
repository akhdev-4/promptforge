"""Authentication & registration business logic.

Orchestrates the user repository and security primitives. Knows nothing about
HTTP — it raises domain errors that the API layer translates.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.exceptions import AuthenticationError, ConflictError
from app.models.user import User, UserRole
from app.repositories.user import UserRepository
from app.schemas.auth import Token
from app.schemas.user import UserCreate


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.users = UserRepository(session)

    async def register(self, data: UserCreate) -> User:
        if await self.users.email_exists(data.email):
            raise ConflictError("An account with this email already exists")

        username = data.username
        if username and await self.users.username_exists(username):
            raise ConflictError("This username is already taken")

        user = await self.users.create(
            email=str(data.email).lower(),
            username=username,
            full_name=data.full_name,
            hashed_password=security.hash_password(data.password),
            role=UserRole.CONTRIBUTOR,
            is_active=True,
            is_verified=False,
        )
        return user

    async def authenticate(self, email: str, password: str) -> User:
        user = await self.users.get_by_email(email)
        # Verify against a real-looking hash regardless to reduce timing leakage.
        if user is None or not user.hashed_password:
            security.verify_password(password, security.hash_password("dummy"))
            raise AuthenticationError("Incorrect email or password")
        if not security.verify_password(password, user.hashed_password):
            raise AuthenticationError("Incorrect email or password")
        if not user.is_active:
            raise AuthenticationError("This account is disabled")

        user.last_login_at = datetime.now(timezone.utc)
        await self.session.flush()
        return user

    @staticmethod
    def issue_tokens(user: User) -> Token:
        subject = str(user.id)
        return Token(
            access_token=security.create_access_token(subject),
            refresh_token=security.create_refresh_token(subject),
        )

    async def refresh(self, refresh_token: str) -> Token:
        try:
            payload = security.decode_token(refresh_token, expected_type="refresh")
        except ValueError as exc:
            raise AuthenticationError(str(exc)) from exc

        try:
            user_id = uuid.UUID(str(payload.get("sub")))
        except (ValueError, TypeError) as exc:
            raise AuthenticationError("Invalid refresh token") from exc

        user = await self.users.get(user_id)
        if user is None or not user.is_active:
            raise AuthenticationError("Invalid refresh token")
        return self.issue_tokens(user)
