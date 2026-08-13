from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.accounts.domain.models import Account
from app.dashboard.schemas import (
    DashboardAccount,
    DashboardSummary,
    DashboardTransaction,
)
from app.transactions.domain.models import (
    Transaction,
    TransactionType,
)


class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_dashboard(self, user) -> DashboardSummary:
        income, expenses = self._monthly_summary(user.id)
        savings = income - expenses

        accounts = self._account_balances(user.id)
        net_worth = sum(
            (account.balance for account in accounts),
            start=Decimal("0"),
        )

        recent_transactions = self._recent_transactions(user.id)

        return DashboardSummary(
            net_worth=net_worth,
            income=income,
            expenses=expenses,
            savings=savings,
            health_score=None,
            ai_insight="You're on track this month.",
            accounts=accounts,
            recent_transactions=recent_transactions,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _monthly_summary(
        self,
        user_id,
    ) -> tuple[Decimal, Decimal]:
        current_month = datetime.now(UTC).month
        current_year = datetime.now(UTC).year

        income = (
            self.db.query(
                func.coalesce(func.sum(Transaction.amount), 0)
            )
            .join(Account)
            .filter(
                Account.user_id == user_id,
                Transaction.transaction_type == TransactionType.CREDIT,
                func.extract("month", Transaction.transaction_date)
                == current_month,
                func.extract("year", Transaction.transaction_date)
                == current_year,
            )
            .scalar()
        )

        expenses = (
            self.db.query(
                func.coalesce(func.sum(Transaction.amount), 0)
            )
            .join(Account)
            .filter(
                Account.user_id == user_id,
                Transaction.transaction_type == TransactionType.DEBIT,
                func.extract("month", Transaction.transaction_date)
                == current_month,
                func.extract("year", Transaction.transaction_date)
                == current_year,
            )
            .scalar()
        )

        return income, expenses

    def _account_balances(
        self,
        user_id,
    ) -> list[DashboardAccount]:
        balances = (
            self.db.query(
                Account.id,
                Account.name,
                (
                    Account.opening_balance
                    + func.coalesce(
                        func.sum(
                            case(
                                (
                                    Transaction.transaction_type
                                    == TransactionType.CREDIT,
                                    Transaction.amount,
                                ),
                                else_=-Transaction.amount,
                            )
                        ),
                        0,
                    )
                ).label("balance"),
            )
            .outerjoin(Transaction)
            .filter(Account.user_id == user_id)
            .group_by(
                Account.id,
                Account.name,
                Account.opening_balance,
            )
            .all()
        )

        return [
            DashboardAccount(
                id=account.id,
                name=account.name,
                balance=account.balance,
            )
            for account in balances
        ]

    def _recent_transactions(
        self,
        user_id,
    ) -> list[DashboardTransaction]:
        transactions = (
            self.db.query(Transaction)
            .join(Account)
            .filter(Account.user_id == user_id)
            .order_by(Transaction.transaction_date.desc())
            .limit(5)
            .all()
        )

        return [
            DashboardTransaction(
                id=transaction.id,
                description=transaction.description,
                amount=transaction.amount,
                transaction_type=transaction.transaction_type.value,
                transaction_date=transaction.transaction_date,
            )
            for transaction in transactions
        ]