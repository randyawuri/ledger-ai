from datetime import datetime
from decimal import Decimal

from app.insights.schemas import Insight


class InsightEngine:

    @staticmethod
    def generate(
        monthly_income: Decimal,
        monthly_expenses: Decimal,
        recent_transactions,
    ) -> list[Insight]:

        insights = []

        if monthly_income > 0:

            savings = monthly_income - monthly_expenses
            savings_rate = (savings / monthly_income) * 100

            if savings_rate >= 20:
                insights.append(
                    Insight(
                        title="Healthy savings",
                        description=(
                            f"You're saving {savings_rate:.0f}% "
                            "of your income this month."
                        ),
                        severity="success",
                    )
                )

            elif savings_rate < 0:
                insights.append(
                    Insight(
                        title="Overspending",
                        description=(
                            "Your expenses exceeded your income "
                            "this month."
                        ),
                        severity="danger",
                    )
                )

            else:
                insights.append(
                    Insight(
                        title="Low savings",
                        description=(
                            f"Only {savings_rate:.0f}% of your "
                            "income remains after expenses."
                        ),
                        severity="warning",
                    )
                )

        for transaction in recent_transactions:

            if transaction.amount >= 100000:

                insights.append(
                    Insight(
                        title="Large transaction",
                        description=(
                            f"You spent "
                            f"₦{transaction.amount:,.2f} "
                            f"on {transaction.description}."
                        ),
                        severity="warning",
                    )
                )

        if not recent_transactions:

            insights.append(
                Insight(
                    title="No recent activity",
                    description="No recent transactions found.",
                    severity="info",
                )
            )

        return insights