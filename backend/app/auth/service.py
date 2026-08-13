from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.auth.schemas import TokenResponse
from app.auth.repository import UserRepository
from app.auth.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.users.domain.models import User


class EmailAlreadyRegisteredError(Exception):
    """Raised when attempting to register an existing email."""


class InvalidCredentialsError(Exception):
    """Raised when authentication credentials are invalid."""


class InactiveUserError(Exception):
    """Raised when an inactive user attempts to authenticate."""


class UserNotFoundError(Exception):
    """Raised when a requested user does not exist."""


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)

    # ---------------------------------------------------------
    # Registration
    # ---------------------------------------------------------

    def register(
        self,
        *,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
    ) -> TokenResponse:
        normalized_email = email.strip().lower()

        if self.users.exists(normalized_email):
            raise EmailAlreadyRegisteredError(
                "An account with this email already exists."
            )

        user = User(
            email=normalized_email,
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            password_hash=hash_password(password),
        )

        self.users.create(user)

        access_token = create_access_token(
            subject=str(user.id),
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
        )

    # ---------------------------------------------------------
    # Login
    # ---------------------------------------------------------

    def login(
        self,
        *,
        email: str,
        password: str,
    ) -> TokenResponse:
        normalized_email = email.strip().lower()

        print("=" * 60)
        print("LOGIN ATTEMPT")
        print(f"Email entered: {normalized_email}")

        user = self.users.get_by_email(normalized_email)

        print(f"User found: {user is not None}")

        if user is None:
            print("❌ User lookup failed.")
            print("=" * 60)

            raise InvalidCredentialsError(
                "Invalid email or password."
            )

        print(f"Database email : {user.email}")
        print(f"User ID        : {user.id}")

        if hasattr(user, "is_active"):
            print(f"Is Active      : {user.is_active}")

        print(f"Password hash  : {user.password_hash}")

        try:
            password_ok = verify_password(
                password,
                user.password_hash,
            )
            print(f"Password valid : {password_ok}")
        except Exception as exc:
            print("Password verification raised an exception:")
            print(type(exc).__name__)
            print(exc)
            print("=" * 60)
            raise

        if not password_ok:
            print("❌ Password verification failed.")
            print("=" * 60)

            raise InvalidCredentialsError(
                "Invalid email or password."
            )

        if hasattr(user, "is_active") and not user.is_active:
            print("❌ User is inactive.")
            print("=" * 60)

            raise InactiveUserError(
                "This account is inactive."
            )

        if hasattr(user, "last_login"):
            user.last_login = datetime.now(timezone.utc)
            self.users.update(user)

        access_token = create_access_token(
            subject=str(user.id),
        )

        print("✅ Login successful.")
        print("=" * 60)

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
        )

    # ---------------------------------------------------------
    # Current User
    # ---------------------------------------------------------

    def get_user(
        self,
        user_id: UUID,
    ) -> User:
        user = self.users.get_by_id(user_id)

        if user is None:
            raise UserNotFoundError(
                "User not found."
            )

        return user