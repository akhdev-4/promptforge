"""Authentication endpoints: register, login, refresh."""

from __future__ import annotations

import contextlib
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import CurrentUser, DbSession
from app.core.ratelimit import rate_limit
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RefreshRequest,
    ResetPasswordRequest,
    Token,
)
from app.schemas.user import UserCreate, UserRead
from app.services.account import AccountService
from app.services.auth import AuthService

router = APIRouter()

# Token-minting endpoints are throttled by IP: they email real people and are
# the obvious target for enumeration and mail-flooding.
_email_throttle = Depends(rate_limit("auth_email", "RATE_LIMIT_AUTH_EMAIL_PER_MIN"))


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new account",
)
async def register(data: UserCreate, db: DbSession) -> UserRead:
    service = AuthService(db)
    user = await service.register(data)
    # Best-effort: a mail failure must not fail the registration.
    with contextlib.suppress(Exception):
        await AccountService(db).send_verification(user)
    return UserRead.model_validate(user)


@router.post(
    "/verify-email/resend",
    response_model=MessageResponse,
    dependencies=[_email_throttle],
    summary="Resend the email-confirmation link",
)
async def resend_verification(db: DbSession, user: CurrentUser) -> MessageResponse:
    sent = await AccountService(db).send_verification(user)
    return MessageResponse(detail=f"Confirmation link sent to {user.email}.", email_sent=sent)


@router.post(
    "/verify-email",
    response_model=UserRead,
    summary="Confirm an email address with the emailed token",
)
async def verify_email(token: str, db: DbSession) -> UserRead:
    user = await AccountService(db).verify_email(token)
    return UserRead.model_validate(user)


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    dependencies=[_email_throttle],
    summary="Email a password-reset link",
)
async def forgot_password(data: ForgotPasswordRequest, db: DbSession) -> MessageResponse:
    sent = await AccountService(db).request_password_reset(data.email)
    # Deliberately identical whether or not the account exists, so this can't be
    # used to discover which addresses are registered.
    return MessageResponse(
        detail="If that email has an account, a reset link is on its way.",
        email_sent=sent,
    )


@router.post(
    "/reset-password",
    response_model=Token,
    summary="Set a new password using the emailed token",
)
async def reset_password(data: ResetPasswordRequest, db: DbSession) -> Token:
    service = AccountService(db)
    user = await service.reset_password(data.token, data.password)
    # Log them straight in — they've just proven control of the inbox.
    return AuthService(db).issue_tokens(user)


@router.post("/login", response_model=Token, summary="Log in (OAuth2 form)")
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbSession,
) -> Token:
    """OAuth2 password flow so Swagger's *Authorize* button works.

    The ``username`` field carries the user's email.
    """
    service = AuthService(db)
    user = await service.authenticate(form.username, form.password)
    return service.issue_tokens(user)


@router.post("/login/json", response_model=Token, summary="Log in (JSON body)")
async def login_json(data: LoginRequest, db: DbSession) -> Token:
    service = AuthService(db)
    user = await service.authenticate(str(data.email), data.password)
    return service.issue_tokens(user)


@router.post("/refresh", response_model=Token, summary="Exchange a refresh token")
async def refresh(data: RefreshRequest, db: DbSession) -> Token:
    return await AuthService(db).refresh(data.refresh_token)
