from sqlalchemy import extract
from datetime import datetime
from datetime import timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.accounts.domain.models import Account
from app.forecasting.engine import ForecastEngine
from app.transactions.domain.models import Transaction
from app.transactions.domain.models import TransactionType


class ForecastService:

    def __init__(self, db: Session):
        self.db = db
        self.engine = ForecastEngine()

    def get_forecast(self, user):

        current_month = extract(
            "month",
            func.now(),
        )

        current_year = extract(
            "year",
            func.now(),
        )

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

        opening = (
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

        current_balance = (
            opening
            + income
            - expenses
        )

        daily_income = income / 30
        daily_expense = expenses / 30

        forecast = self.engine.forecast(
            current_balance,
            daily_income,
            daily_expense,
        )

        return {
            "current_balance": current_balance,
            "predicted_balance": forecast[-1]["projected_balance"],
            "days_forecasted": 30,
            "forecast": forecast,
        }