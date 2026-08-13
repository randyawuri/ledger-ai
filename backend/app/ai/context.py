import json

from app.analytics.service import AnalyticsService
from app.dashboard.service import DashboardService
from app.forecasting.service import ForecastService
from app.health.service import FinancialHealthService


class ContextBuilder:

    def __init__(self, db):
        self.db = db

    def build(self, user):

        dashboard = DashboardService(self.db).get_dashboard(user)

        analytics = AnalyticsService(self.db).get_analytics(user)

        forecast = ForecastService(self.db).get_forecast(user)

        health = FinancialHealthService(self.db).get_health(user)

        context = {
            "dashboard": dashboard,
            "analytics": analytics,
            "forecast": forecast,
            "financial_health": health,
        }

        return json.dumps(
            context,
            default=str,
            indent=2,
        )