from sqlalchemy import extract
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.accounts.domain.models import Account
from app.budgets.domain.models import Budget
from app.health.scoring import FinancialHealthScorer
from app.transactions.domain.models import Transaction
from app.transactions.domain.models import TransactionType


class FinancialHealthService:

    def __init__(self, db: Session):
        self.db = db
        self.scorer = FinancialHealthScorer()

    def get_health(self, user):

        current_month = extract(
            "month",
            func.now(),
        )

        current_year = extract(
            "year",
            func.now(),
        )

        #
        # Monthly income
        #

        income = (
            self.db.query(
                func.coalesce(
                    func.sum(Transaction.amount),
                    0,
                )
            )
            .join(Account)
            .filter(
                Account.user_id == user.id,
                Transaction.transaction_type == TransactionType.CREDIT,
                extract(
                    "month",
                    Transaction.transaction_date,
                ) == current_month,
                extract(
                    "year",
                    Transaction.transaction_date,
                ) == current_year,
            )
            .scalar()
        )

        #
        # Monthly expenses
        #

        expenses = (
            self.db.query(
                func.coalesce(
                    func.sum(Transaction.amount),
                    0,
                )
            )
            .join(Account)
            .filter(
                Account.user_id == user.id,
                Transaction.transaction_type == TransactionType.DEBIT,
                extract(
                    "month",
                    Transaction.transaction_date,
                ) == current_month,
                extract(
                    "year",
                    Transaction.transaction_date,
                ) == current_year,
            )
            .scalar()
        )

        #
        # Total budget
        #

        total_budget = (
            self.db.query(
                func.coalesce(
                    func.sum(Budget.amount),
                    0,
                )
            )
            .filter(
                Budget.user_id == user.id,
            )
            .scalar()
        )

        if total_budget > 0:
            budget_used = float(
                expenses / total_budget * 100
            )
        else:
            budget_used = 0

        #
        # Current cash
        #

        opening_balance = (
            self.db.query(
                func.coalesce(
                    func.sum(Account.opening_balance),
                    0,
                )
            )
            .filter(
                Account.user_id == user.id,
            )
            .scalar()
        )

        #
        # Approximate current balance
        #

        current_balance = (
            opening_balance
            + income
            - expenses
        )

        #
        # Emergency fund
        #

        if expenses > 0:
            emergency_months = float(
                current_balance / expenses
            )
        else:
            emergency_months = 6

        return self.scorer.score(
            income=income,
            expenses=expenses,
            budget_used=budget_used,
            emergency_months=emergency_months,
        )