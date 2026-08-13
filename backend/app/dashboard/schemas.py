from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class DashboardAccount(BaseModel):
    id: UUID
    name: str
    balance: Decimal


class DashboardTransaction(BaseModel):
    id: UUID
    description: str
    amount: Decimal
    transaction_type: str
    transaction_date: datetime


class CashflowPoint(BaseModel):
    month: str
    income: Decimal
    expenses: Decimal


class GoalSummary(BaseModel):
    id: UUID
    name: str
    progress: float


class UpcomingBill(BaseModel):
    id: UUID
    name: str
    amount: Decimal
    due_date: datetime


class DashboardSummary(BaseModel):
    net_worth: Decimal

    income: Decimal
    expenses: Decimal
    savings: Decimal

    health_score: int | None

    ai_insight: str | None

    accounts: list[DashboardAccount]

    recent_transactions: list[DashboardTransaction]

    monthly_cashflow: list[CashflowPoint]

    goals: list[GoalSummary]

    upcoming_bills: list[UpcomingBill]