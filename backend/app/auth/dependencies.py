from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.auth.security import get_subject_from_token
from app.auth.service import AuthService, UserNotFoundError
from app.db.session import get_db
from app.users.domain.models import User


# ---------------------------------------------------------
# OAuth2
# ---------------------------------------------------------

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token",
)


# ---------------------------------------------------------
# Current User
# ---------------------------------------------------------

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )

    # -----------------------------------------------------
    # Decode JWT
    # -----------------------------------------------------

    try:
        subject = get_subject_from_token(token)

        user_id = UUID(subject)

    except (JWTError, ValueError, TypeError):
        raise credentials_exception

    # -----------------------------------------------------
    # Load User
    # -----------------------------------------------------

    service = AuthService(db)

    try:
        user = service.get_user(user_id)

    except UserNotFoundError:
        raise credentials_exception

    # -----------------------------------------------------
    # Safety check
    # -----------------------------------------------------

    if user is None:
        raise credentials_exception

    # -----------------------------------------------------
    # Active user check
    # -----------------------------------------------------

    if hasattr(user, "is_active") and not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user.",
        )

    return user