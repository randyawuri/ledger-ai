from sqlalchemy.orm import Session

from app.dashboard.service import DashboardService
from app.forecasting.service import ForecastService
from app.insights.service import InsightService
from app.health.service import HealthService


class ContextBuilder:

    def __init__(self, db: Session):
        self.dashboard = DashboardService(db)
        self.forecast = ForecastService(db)
        self.health = HealthService(db)
        self.insights = InsightService(db)

    def build(self, user):

        return {

            "dashboard":
                self.dashboard.get_dashboard(user),

            "forecast":
                self.forecast.get_forecast(user),

            "health":
                self.health.get_health(user),

            "insights":
                self.insights.get_insights(user),
        }