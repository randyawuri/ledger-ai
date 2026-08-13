from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.schemas import (
    CurrentUserResponse,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
)
from app.auth.service import (
    AuthService,
    EmailAlreadyRegisteredError,
    InactiveUserError,
    InvalidCredentialsError,
)
from app.db.session import get_db
from app.users.domain.models import User


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# =========================================================
# Register
# =========================================================

@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    try:
        token = service.register(
            email=payload.email,
            password=payload.password,
            first_name=payload.first_name,
            last_name=payload.last_name,
        )

        db.commit()

        return token

    except EmailAlreadyRegisteredError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


# =========================================================
# Login — JSON API
# =========================================================

@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    """
    Standard JSON login endpoint.

    Expects:

    {
        "email": "user@example.com",
        "password": "password"
    }
    """

    service = AuthService(db)

    try:
        token = service.login(
            email=payload.email,
            password=payload.password,
        )

        db.commit()

        return token

    except InvalidCredentialsError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    except InactiveUserError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )


# =========================================================
# OAuth2 Token — Swagger
# =========================================================

@router.post(
    "/token",
    response_model=TokenResponse,
)
def token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    OAuth2-compatible login endpoint.

    Used by Swagger's Authorize button.

    OAuth2 sends:

        username = email address
        password = password
    """

    service = AuthService(db)

    try:
        token_response = service.login(
            email=form_data.username,
            password=form_data.password,
        )

        db.commit()

        return token_response

    except InvalidCredentialsError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    except InactiveUserError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )


# =========================================================
# Current User
# =========================================================

@router.get(
    "/me",
    response_model=CurrentUserResponse,
)
def me(
    current_user: User = Depends(get_current_user),
):
    """
    Return the currently authenticated user.
    """

    return current_user