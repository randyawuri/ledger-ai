from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.transactions.domain.models import TransactionType


class ImportedTransaction(BaseModel):
    transaction_date: datetime
    description: str
    amount: Decimal
    balance: Decimal
    transaction_type: TransactionType
    merchant: str | None = None


class ImportedTransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    transaction_date: datetime
    description: str
    amount: Decimal
    transaction_type: TransactionType
    balance: Decimal | None


class ImportCommitRequest(BaseModel):
    account_id: UUID