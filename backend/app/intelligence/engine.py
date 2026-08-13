from sqlalchemy.orm import Session

from app.analytics.service import AnalyticsService
from app.budgets.service import BudgetService
from app.forecasting.service import ForecastService
from app.goals.service import GoalService
from app.health.service import HealthService


class IntelligenceEngine:
    """
    Central orchestrator for Ledger AI.

    It aggregates financial intelligence from all
    domain services and exposes a unified interface
    to AI, Dashboard, Notifications and Reporting.
    """

    def __init__(self, db: Session):
        self.db = db

        self.analytics = AnalyticsService(db)
        self.budgets = BudgetService(db)
        self.forecasting = ForecastService(db)
        self.goals = GoalService(db)
        self.health = HealthService(db)

    def build_context(self, user) -> dict:
        """
        Build the complete financial context for a user.
        """

        analytics = self.analytics.get_analytics(user)

        return {
            "analytics": analytics,
            "budgets": self.budgets.budget_status(user),
            "forecast": self.forecasting.forecast(user),
            "goals": self.goals.progress(user),
            "health": self.health.summary(user),
        }

    def summary(self, user) -> dict:
        """
        Lightweight summary used by dashboards,
        AI assistants and notifications.
        """

        context = self.build_context(user)
        analytics = context["analytics"]

        return {
            "net_worth": analytics["net_worth"],
            "cashflow": analytics["cashflow"],
            "health": context["health"],
            "forecast": context["forecast"],
        }

    def insights(self, user) -> list[dict]:
        """
        Placeholder for deterministic financial insights.

        This will eventually aggregate insights from:
        - Analytics
        - Budgets
        - Goals
        - Forecasting
        - Health

        Returns:
            List of structured insight dictionaries.
        """
        return []