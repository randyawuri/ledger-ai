from decimal import Decimal
from datetime import datetime, date

from pydantic import BaseModel


class CashFlowForecast(BaseModel):
    current_balance: Decimal
    expected_income: Decimal
    expected_expenses: Decimal
    projected_balance: Decimal
    forecast_until: datetime

class ForecastPoint(BaseModel):
    date: date
    projected_balance: Decimal

class ForecastResponse(BaseModel):
    current_balance: Decimal
    predicted_balance: Decimal
    days_forecasted: int
    forecast: list[ForecastPoint]