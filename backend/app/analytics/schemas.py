from decimal import Decimal

from pydantic import BaseModel


class CategorySpending(BaseModel):
    category: str
    amount: Decimal


class MonthlyCashflow(BaseModel):
    income: Decimal
    expenses: Decimal
    net: Decimal


class MonthlyTrend(BaseModel):
    month: str
    income: Decimal
    expenses: Decimal


class LargestTransaction(BaseModel):
    id: str
    description: str
    merchant: str | None
    amount: Decimal
    transaction_type: str


class AnalyticsResponse(BaseModel):
    net_worth: Decimal
    cashflow: MonthlyCashflow
    spending: list[CategorySpending]
    trends: list[MonthlyTrend]