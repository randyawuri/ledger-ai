from decimal import Decimal

from sqlalchemy import extract
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import insights
from app.accounts.domain.models import Account
from app.budgets.domain.models import Budget
from app.categories.domain.models import Category
from app.insights import engine
from app.transactions.domain.models import Transaction
from app.common.enums import TransactionType
from app.dashboard.service import DashboardService
from app.insights.engine import InsightEngine



class InsightService:

    def __init__(self, db: Session):
        self.db = db

    def get_insights(self, user):

        insights = []

        current_month = extract(
            "month",
            func.now(),
        )

        current_year = extract(
            "year",
            func.now(),
        )

        #
        # Income
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
        # Expenses
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

        if income > expenses:

            insights.append(
                {
                    "severity": "success",
                    "title": "Positive Cash Flow",
                    "description": (
                        f"Your income exceeded expenses "
                        f"by ₦{income-expenses:,.2f} this month."
                    ),
                }
            )

        else:

            insights.append(
                {
                    "severity": "warning",
                    "title": "Negative Cash Flow",
                    "description": (
                        f"You spent ₦{expenses-income:,.2f} "
                        f"more than you earned this month."
                    ),
                }
            )

        #
        # Budget warnings
        #

        budgets = (
            self.db.query(Budget)
            .filter(
                Budget.user_id == user.id,
            )
            .all()
        )

        for budget in budgets:

            spent = (
                self.db.query(
                    func.coalesce(
                        func.sum(Transaction.amount),
                        0,
                    )
                )
                .join(Account)
                .filter(
                    Account.user_id == user.id,
                    Transaction.category_id == budget.category_id,
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

            percent = (
                float(spent / budget.amount * 100)
                if budget.amount > 0
                else 0
            )

            if percent >= 80:

                category = (
                    self.db.query(Category)
                    .filter(
                        Category.id == budget.category_id
                    )
                    .first()
                )

                insights.append(
                    {
                        "severity": "warning",
                        "title": "Budget Alert",
                        "description": (
                            f"You've used "
                            f"{percent:.0f}% of your "
                            f"{category.name} budget."
                        ),
                    }
                )

        #
        # Largest expense category
        #

        largest = (
            self.db.query(
                Category.name,
                func.sum(Transaction.amount).label(
                    "total"
                ),
            )
            .join(
                Transaction,
                Category.id == Transaction.category_id,
            )
            .join(
                Account,
                Transaction.account_id == Account.id,
            )
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
            .group_by(Category.name)
            .order_by(func.sum(Transaction.amount).desc())
            .first()
        )

        if largest:

            insights.append(
                {
                    "severity": "info",
                    "title": "Largest Expense",
                    "description": (
                        f"{largest.name} is your "
                        f"largest expense category "
                        f"this month."
                    ),
                }
            )

        dashboard = DashboardService(self.db).get_dashboard(user)
        
        engine = InsightEngine()

        ai_insights = engine.generate(
            monthly_income=income,
            monthly_expenses=expenses,
            recent_transactions=dashboard.recent_transactions,
        )

        insights.extend(
            [insight.model_dump() for insight in ai_insights]
        )
        return insights