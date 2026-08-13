from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.users.domain.models import User


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(
        self,
        email: str,
        first_name: str,
        last_name: str,
        password: str,
    ):
        existing = (
            self.db.query(User)
            .filter(User.email == email)
            .first()
        )

        if existing:
            raise ValueError("Email already registered")

        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password_hash=hash_password(password),
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def authenticate(
        self,
        email: str,
        password: str,
    ):
        user = (
            self.db.query(User)
            .filter(User.email == email)
            .first()
        )

        if not user:
            return None

        if not verify_password(password, user.password_hash):
            return None

        token = create_access_token(user.id)

        return token