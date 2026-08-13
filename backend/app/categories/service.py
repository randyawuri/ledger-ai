from uuid import UUID

from sqlalchemy.orm import Session

from app.categories.domain.models import (
    Category,
    TransactionType,
)


class CategoryService:
    def __init__(self, db: Session):
        self.db = db

    def create_category(
        self,
        user,
        name: str,
        transaction_type: TransactionType,
        icon: str,
        color: str,
    ):
        category = Category(
            user_id=user.id,
            name=name,
            transaction_type=transaction_type,
            icon=icon,
            color=color,
        )

        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)

        return category

    def get_categories(self, user):
        return (
            self.db.query(Category)
            .filter(Category.user_id == user.id)
            .all()
        )

    def get_category(
        self,
        user,
        category_id: UUID,
    ):
        return (
            self.db.query(Category)
            .filter(
                Category.id == category_id,
                Category.user_id == user.id,
            )
            .first()
        )