from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.users.domain.models import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    # ---------------------------------------------------------
    # Queries
    # ---------------------------------------------------------

    def get_by_id(
        self,
        user_id: UUID,
    ) -> User | None:

        return self.db.get(User, user_id)

    def get_by_email(
        self,
        email: str,
    ) -> User | None:

        stmt = (
            select(User)
            .where(User.email == email.lower())
        )

        return self.db.scalar(stmt)
    
    def exists(
        self,
        email: str,
    ) -> bool:

        stmt = (
            select(User.id)
            .where(User.email == email.lower())
        )

        return self.db.scalar(stmt) is not None

    # ---------------------------------------------------------
    # Commands
    # ---------------------------------------------------------

    def create(
        self,
        user: User,
    ) -> User:

        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)

        return user

    def update(
        self,
        user: User,
    ) -> User:

        self.db.flush()
        self.db.refresh(user)

        return user