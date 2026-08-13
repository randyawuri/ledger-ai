from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


# ---------------------------------------------------------
# Password Hashing
# ---------------------------------------------------------


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    """Hash a plaintext password."""
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    password_hash_value: str,
) -> bool:
    """Verify a plaintext password against its hash."""
    return password_hash.verify(
        plain_password,
        password_hash_value,
    )


# ---------------------------------------------------------
# JWT
# ---------------------------------------------------------

def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a signed JWT access token.

    Args:
        subject: Usually the user's UUID.
        expires_delta: Optional custom expiration.

    Returns:
        Encoded JWT.
    """

    if expires_delta is None:
        expires_delta = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )

    expire = datetime.now(timezone.utc) + expires_delta

    payload: dict[str, Any] = {
        "sub": str(subject),
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY.get_secret_value(),
        algorithm=settings.ALGORITHM,
    )


def decode_access_token(
    token: str,
) -> dict[str, Any]:
    """
    Decode and validate a JWT.

    Raises:
        JWTError if the token is invalid or expired.
    """

    return jwt.decode(
        token,
        settings.SECRET_KEY.get_secret_value(),
        algorithms=[settings.ALGORITHM],
    )


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def get_subject_from_token(
    token: str,
) -> str:
    """
    Extract the user ID from a JWT.
    """

    payload = decode_access_token(token)

    subject = payload.get("sub")

    if subject is None:
        raise JWTError("Missing subject.")

    return str(subject)