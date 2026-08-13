from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from decimal import Decimal


@dataclass(slots=True)
class Account:
    id: UUID
    user_id: UUID
    name: str
    institution: str
    currency: str
    opening_balance: Decimal
    current_balance: Decimal
    created_at: datetime