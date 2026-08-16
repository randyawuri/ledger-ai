from datetime import date
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.accounts.domain.models import Account
from app.budgets.domain.models import Budget
from app.categories.domain.models import Category
from app.transactions.domain.models import (
    Transaction,
    TransactionType,
)


class BudgetRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, budget: Budget):
        self.db.add(budget)
        return budget

    def get(self, budget_id: UUID):
        return (
            self.db.query(Budget)
            .filter(Budget.id == budget_id)
            .first()
        )

    def list_by_user(self, user_id: UUID):
        return (
            self.db.query(Budget)
            .filter(Budget.user_id == user_id)
            .all()
        )

    def delete(self, budget: Budget):
        self.db.delete(budget)

    def total_spent(
        self,
        user_id: UUID,
        category_id: UUID,
        start_date: date,
        end_date: date,
    ):
        return (
            self.db.query(
                func.coalesce(func.sum(Transaction.amount), 0)
            )
            .join(Account)
            .filter(
                Account.user_id == user_id,
                Transaction.category_id == category_id,
                Transaction.transaction_type == TransactionType.DEBIT,
                func.date(Transaction.transaction_date) >= start_date,
                func.date(Transaction.transaction_date) <= end_date,
            )
            .scalar()
        )

    def get_category_for_user(
        self,
        category_id: UUID,
        user_id: UUID,
    ):
        return (
            self.db.query(Category)
            .filter(
                Category.id == category_id,
                Category.user_id == user_id,
            )
            .first()
        )