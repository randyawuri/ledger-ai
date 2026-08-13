from uuid import UUID

from app.analytics.repository import AnalyticsRepository
from app.analytics.schemas import (
    AnalyticsResponse,
    MonthlyCashflow,
    CategorySpending,
)


class AnalyticsService:
    def __init__(self, db):
        self.repo = AnalyticsRepository(db)

    def monthly_cashflow(self, user_id: UUID) -> MonthlyCashflow:
        income = self.repo.monthly_income(user_id)
        expenses = self.repo.monthly_expenses(user_id)

        return MonthlyCashflow(
            income=income,
            expenses=expenses,
            net=income - expenses,
        )

    def net_worth(self, user_id: UUID):
        opening = self.repo.total_opening_balance(user_id)
        income = self.repo.total_income(user_id)
        expenses = self.repo.total_expenses(user_id)

        return opening + income - expenses

    def spending_by_category(
        self,
        user_id: UUID,
    ) -> list[CategorySpending]:

        rows = self.repo.spending_by_category(user_id)

        return [
            CategorySpending(
                category=row.name,
                amount=row.amount,
            )
            for row in rows
        ]

    def monthly_trends(self, user_id: UUID):
        return self.repo.monthly_trends(user_id)

    def summary(self, user_id: UUID) -> AnalyticsResponse:
        return AnalyticsResponse(
            net_worth=self.net_worth(user_id),
            cashflow=self.monthly_cashflow(user_id),
            spending=self.spending_by_category(user_id),
            trends=self.monthly_trends(user_id),
        )