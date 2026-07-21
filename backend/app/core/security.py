"""Security primitives: password hashing and JWT encode/decode.

Kept dependency-light and framework-agnostic so both the auth service and
tests can use it without importing FastAPI.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Literal

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

TokenType = Literal["access", "refresh"]


# --- Passwords ---------------------------------------------------------------
# We call ``bcrypt`` directly rather than through passlib: passlib is
# unmaintained and couples to bcrypt's internals, which breaks whenever the
# deployed bcrypt version drifts. bcrypt's own API is small and stable, and it
# still produces/consumes standard ``$2b$`` hashes, so existing passwords stay
# valid. bcrypt only uses the first 72 bytes and raises past that, so we
# truncate the encoded password defensively.
def hash_password(plain: str) -> str:
    pw = plain.encode("utf-8")[:72]
    return bcrypt.hashpw(pw, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8")[:72], hashed.encode("utf-8"))
    except ValueError:
        # Malformed/legacy hash — treat as a non-match rather than 500.
        return False


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
