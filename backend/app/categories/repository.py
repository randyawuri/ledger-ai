from sqlalchemy import select

from app.categories.domain.models import Category
from app.db.repositories import BaseRepository


class CategoryRepository(BaseRepository):

    def create(self, category):
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def get(self, category_id):
        return self.db.get(Category, category_id)

    def list(self):
        stmt = select(Category)
        return self.db.scalars(stmt).all()

    def list_by_type(self, transaction_type):
        stmt = (
            select(Category)
            .where(Category.transaction_type == transaction_type)
        )
        return self.db.scalars(stmt).all()