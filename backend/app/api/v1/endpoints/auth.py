"""Authentication endpoints: register, login, refresh."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import DbSession
from app.schemas.auth import LoginRequest, RefreshRequest, Token
from app.schemas.user import UserCreate, UserRead
from app.services.auth import AuthService

router = APIRouter()


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new account",
)
async def register(data: UserCreate, db: DbSession) -> UserRead:
    user = await AuthService(db).register(data)
    return UserRead.model_validate(user)


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
