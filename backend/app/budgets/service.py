from calendar import monthrange
from datetime import date
from decimal import Decimal
from uuid import UUID

from app.budgets.domain.models import Budget
from app.db.unit_of_work import UnitOfWork


class BudgetService:

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def create_budget(
        self,
        user_id: UUID,
        category_id: UUID,
        name: str,
        amount: Decimal,
    ):
        budget = Budget(
            user_id=user_id,
            category_id=category_id,
            name=name,
            amount=amount,
        )

        self.uow.budgets.create(budget)
        self.uow.commit()

        return budget

    def get_budgets(
        self,
        user_id: UUID,
    ):
        return self.uow.budgets.list_by_user(user_id)

    def budget_status(
        self,
        user_id: UUID,
    ):
        budgets = self.uow.budgets.list_by_user(user_id)

        today = date.today()

        start_date = date(
            today.year,
            today.month,
            1,
        )

        end_date = date(
            today.year,
            today.month,
            monthrange(today.year, today.month)[1],
        )

        results = []

        for budget in budgets:

            spent = self.uow.budgets.total_spent(
                user_id=user_id,
                category_id=budget.category_id,
                start_date=start_date,
                end_date=end_date,
            )

            remaining = Decimal(budget.amount) - Decimal(spent)

            percent = Decimal("0")

            if budget.amount > 0:
                percent = (
                    Decimal(spent)
                    / Decimal(budget.amount)
                    * Decimal("100")
                )

            if percent >= 100:
                status = "OVER"

            elif percent >= 80:
                status = "WARNING"

            else:
                status = "GOOD"

            category = self.uow.budgets.get_category(
                budget.category_id
            )

            results.append(
                {
                    "category": category.name,
                    "budget": budget.amount,
                    "spent": spent,
                    "remaining": remaining,
                    "percent_used": round(float(percent), 2),
                    "status": status,
                }
            )

        return results