from datetime import date
from decimal import Decimal

from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from app.accounts.domain.models import Account
from app.categories.domain.models import Category
from app.transactions.domain.models import (
    Transaction,
    TransactionType,
)


class AnalyticsRepository:
    def __init__(self, db: Session):
        self.db = db

    # ---------- Totals ----------

    def total_income(
        self,
        user_id,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> Decimal:

        query = (
            self.db.query(
                func.coalesce(func.sum(Transaction.amount), 0)
            )
            .join(Account)
            .filter(
                Account.user_id == user_id,
                Transaction.transaction_type == TransactionType.CREDIT,
            )
        )

        if start_date:
            query = query.filter(
                func.date(Transaction.transaction_date) >= start_date
            )

        if end_date:
            query = query.filter(
                func.date(Transaction.transaction_date) <= end_date
            )

        return query.scalar()

    def total_expenses(
        self,
        user_id,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> Decimal:

        query = (
            self.db.query(
                func.coalesce(func.sum(Transaction.amount), 0)
            )
            .join(Account)
            .filter(
                Account.user_id == user_id,
                Transaction.transaction_type == TransactionType.DEBIT,
            )
        )

        if start_date:
            query = query.filter(
                func.date(Transaction.transaction_date) >= start_date
            )

        if end_date:
            query = query.filter(
                func.date(Transaction.transaction_date) <= end_date
            )

        return query.scalar()

    def total_opening_balance(
        self,
        user_id,
    ) -> Decimal:

        return (
            self.db.query(
                func.coalesce(
                    func.sum(Account.opening_balance),
                    0,
                )
            )
            .filter(Account.user_id == user_id)
            .scalar()
        )

    # ---------- Category Analytics ----------

    def spending_by_category(
        self,
        user_id,
    ):

        return (
            self.db.query(
                Category.name,
                func.coalesce(
                    func.sum(Transaction.amount),
                    0,
                ).label("amount"),
            )
            .join(
                Transaction,
                Transaction.category_id == Category.id,
            )
            .join(
                Account,
                Transaction.account_id == Account.id,
            )
            .filter(
                Account.user_id == user_id,
                Transaction.transaction_type == TransactionType.DEBIT,
            )
            .group_by(Category.name)
            .order_by(func.sum(Transaction.amount).desc())
            .all()
        )

    # ---------- Merchant Analytics ----------

    def spending_by_merchant(
        self,
        user_id,
    ):

        return (
            self.db.query(
                Transaction.merchant,
                func.coalesce(
                    func.sum(Transaction.amount),
                    0,
                ).label("amount"),
            )
            .join(Account)
            .filter(
                Account.user_id == user_id,
                Transaction.transaction_type == TransactionType.DEBIT,
            )
            .group_by(Transaction.merchant)
            .order_by(func.sum(Transaction.amount).desc())
            .all()
        )

    # ---------- Trends ----------

    def monthly_trends(
        self,
        user_id,
    ):

        return (
            self.db.query(
                extract(
                    "year",
                    Transaction.transaction_date,
                ).label("year"),

                extract(
                    "month",
                    Transaction.transaction_date,
                ).label("month"),

                Transaction.transaction_type,

                func.coalesce(
                    func.sum(Transaction.amount),
                    0,
                ).label("total"),
            )
            .join(Account)
            .filter(Account.user_id == user_id)
            .group_by(
                extract(
                    "year",
                    Transaction.transaction_date,
                ),
                extract(
                    "month",
                    Transaction.transaction_date,
                ),
                Transaction.transaction_type,
            )
            .order_by(
                extract(
                    "year",
                    Transaction.transaction_date,
                ),
                extract(
                    "month",
                    Transaction.transaction_date,
                ),
            )
            .all()
        )

    # ---------- Largest Transactions ----------

    def largest_transactions(
        self,
        user_id,
        limit: int = 10,
    ):

        return (
            self.db.query(Transaction)
            .join(Account)
            .filter(Account.user_id == user_id)
            .order_by(Transaction.amount.desc())
            .limit(limit)
            .all()
        )

    # ---------- Recent Transactions ----------

    def recent_transactions(
        self,
        user_id,
        limit: int = 10,
    ):

        return (
            self.db.query(Transaction)
            .join(Account)
            .filter(Account.user_id == user_id)
            .order_by(
                Transaction.transaction_date.desc()
            )
            .limit(limit)
            .all()
        )