"""Domain-level exceptions and their HTTP translation.

Services raise these framework-agnostic errors; a single set of handlers
registered on the app maps them to consistent JSON responses. This keeps the
service layer free of FastAPI imports (dependency inversion).
"""

from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base application error."""

    status_code: int = status.HTTP_400_BAD_REQUEST
    code: str = "app_error"

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.__class__.__doc__ or "Application error"
        super().__init__(self.message)


class NotFoundError(AppError):
    """The requested resource was not found."""

    status_code = status.HTTP_404_NOT_FOUND
    code = "not_found"


class ConflictError(AppError):
    """The resource conflicts with an existing one."""

    status_code = status.HTTP_409_CONFLICT
    code = "conflict"


class AuthenticationError(AppError):
    """Authentication failed or credentials are invalid."""

    status_code = status.HTTP_401_UNAUTHORIZED
    code = "authentication_error"


class PermissionDeniedError(AppError):
    """You do not have permission to perform this action."""

    status_code = status.HTTP_403_FORBIDDEN
    code = "permission_denied"


class ValidationError(AppError):
    """The request payload is invalid."""

    status_code = 422
    code = "validation_error"


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        headers = {}
        if isinstance(exc, AuthenticationError):
            headers["WWW-Authenticate"] = "Bearer"
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "code": exc.code},
            headers=headers,
        )
