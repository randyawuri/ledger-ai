from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.repositories import BaseRepository
from app.users.models import User


class UserRepository(BaseRepository):

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id):
        return self.db.get(User, user_id)

    def get_by_email(self, email: str):
        stmt = select(User).where(User.email == email)
        return self.db.scalar(stmt)

    def list(self):
        stmt = select(User)
        return self.db.scalars(stmt).all()

    def delete(self, user: User):
        self.db.delete(user)
        self.db.commit()