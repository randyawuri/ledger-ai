from decimal import Decimal
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class RecurringTransaction(BaseModel):
    description: str
    merchant: str | None
    transaction_type: str
    average_amount: Decimal
    occurrences: int
    last_seen: datetime
    estimated_next: datetime

class RecurringPrediction(BaseModel):
    merchant: str
    average_amount: Decimal
    frequency: str
    next_due: datetime
    confidence: float


class RecurringResponse(BaseModel):
    recurring: list[RecurringPrediction]