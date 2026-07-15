"""Security primitives: password hashing and JWT encode/decode.

Kept dependency-light and framework-agnostic so both the auth service and
tests can use it without importing FastAPI.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Literal

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

TokenType = Literal["access", "refresh"]


# --- Passwords ---------------------------------------------------------------
def hash_password(plain: str) -> str:
    # bcrypt only considers the first 72 bytes; truncate defensively so longer
    # passwords don't raise on some backends.
    return _pwd_context.hash(plain[:72])


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(plain[:72], hashed)


# --- JWT ---------------------------------------------------------------------
def _create_token(subject: str, token_type: TokenType, expires_delta: timedelta) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(subject: str) -> str:
    return _create_token(
        subject, "access", timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )


def create_refresh_token(subject: str) -> str:
    return _create_token(
        subject, "refresh", timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    )


def decode_token(token: str, *, expected_type: TokenType | None = None) -> dict[str, Any]:
    """Decode and validate a JWT.

    Raises ``ValueError`` on any invalid/expired token or type mismatch so
    callers can translate to the appropriate HTTP error.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError as exc:
        raise ValueError("Invalid or expired token") from exc

    if expected_type is not None and payload.get("type") != expected_type:
        raise ValueError(f"Expected {expected_type} token")
    return payload
