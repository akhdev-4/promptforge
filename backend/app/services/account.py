"""Email verification and password reset.

Both flows share one shape: mint a single-use, expiring token, email a link, and
consume the token on confirmation. Only a digest of the token is persisted, so
the database alone can't be used to forge a link.
"""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.config import settings
from app.core.email import send_email
from app.core.email_templates import password_reset_email, verify_email
from app.core.exceptions import ConflictError, NotFoundError
from app.models.auth_token import AuthToken, TokenPurpose
from app.models.user import User
from app.repositories.base import BaseRepository
from app.repositories.user import UserRepository


def _display_name(user: User) -> str:
    return user.full_name or user.username or user.email.split("@")[0]


class AccountService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.tokens = BaseRepository(AuthToken, session)
        self.users = UserRepository(session)

    # --- token helpers -------------------------------------------------------
    @staticmethod
    def _is_expired(expires_at: datetime) -> bool:
        # SQLite hands back naive datetimes; stored times are UTC.
        aware = expires_at if expires_at.tzinfo else expires_at.replace(tzinfo=timezone.utc)
        return aware < datetime.now(timezone.utc)

    async def _issue(
        self, user: User, purpose: TokenPurpose, lifetime: timedelta
    ) -> str:
        """Invalidate any outstanding tokens of this purpose, then mint a new one."""
        outstanding = (
            await self.session.execute(
                select(AuthToken).where(
                    AuthToken.user_id == user.id,
                    AuthToken.purpose == purpose,
                    AuthToken.used_at.is_(None),
                )
            )
        ).scalars().all()
        now = datetime.now(timezone.utc)
        for token in outstanding:
            token.used_at = now
            self.session.add(token)

        raw = secrets.token_urlsafe(32)
        await self.tokens.create(
            user_id=user.id,
            purpose=purpose,
            hashed_token=security.hash_api_key(raw),
            expires_at=now + lifetime,
        )
        return raw

    async def _consume(self, raw: str, purpose: TokenPurpose) -> User:
        token = await self.tokens.get_by(
            hashed_token=security.hash_api_key(raw), purpose=purpose
        )
        if token is None:
            raise NotFoundError("This link is invalid.")
        if token.used_at is not None:
            raise ConflictError("This link has already been used.")
        if self._is_expired(token.expires_at):
            raise ConflictError("This link has expired.")
        user = await self.users.get(token.user_id)
        if user is None or not user.is_active:
            raise NotFoundError("Account not found.")
        token.used_at = datetime.now(timezone.utc)
        self.session.add(token)
        await self.session.flush()
        return user

    def _link(self, path: str, raw: str) -> str:
        return f"{settings.FRONTEND_URL.rstrip('/')}/{path}/{raw}"

    # --- email verification --------------------------------------------------
    async def send_verification(self, user: User) -> bool:
        """Email a confirmation link. Returns whether it was delivered."""
        if user.is_verified:
            raise ConflictError("This email is already verified.")
        raw = await self._issue(
            user,
            TokenPurpose.EMAIL_VERIFY,
            timedelta(hours=settings.EMAIL_VERIFY_EXPIRE_HOURS),
        )
        subject, text, html = verify_email(
            name=_display_name(user),
            link=self._link("verify-email", raw),
            expires_hours=settings.EMAIL_VERIFY_EXPIRE_HOURS,
        )
        return await send_email(user.email, subject, text=text, html=html)

    async def verify_email(self, raw: str) -> User:
        user = await self._consume(raw, TokenPurpose.EMAIL_VERIFY)
        if not user.is_verified:
            user.is_verified = True
            self.session.add(user)
            await self.session.flush()
        return user

    # --- password reset ------------------------------------------------------
    async def request_password_reset(self, email: str) -> bool:
        """Email a reset link if the address exists.

        Always reports success to the caller so the endpoint can't be used to
        discover which email addresses have accounts.
        """
        user = await self.users.get_by_email(email)
        if user is None or not user.is_active:
            return False
        raw = await self._issue(
            user,
            TokenPurpose.PASSWORD_RESET,
            timedelta(minutes=settings.PASSWORD_RESET_EXPIRE_MINUTES),
        )
        subject, text, html = password_reset_email(
            name=_display_name(user),
            link=self._link("reset-password", raw),
            expires_minutes=settings.PASSWORD_RESET_EXPIRE_MINUTES,
        )
        return await send_email(user.email, subject, text=text, html=html)

    async def reset_password(self, raw: str, new_password: str) -> User:
        user = await self._consume(raw, TokenPurpose.PASSWORD_RESET)
        user.hashed_password = security.hash_password(new_password)
        # Confirming control of the inbox also proves the address is real.
        user.is_verified = True
        self.session.add(user)
        await self.session.flush()
        return user
