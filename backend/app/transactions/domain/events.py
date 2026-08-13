from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class TransactionCreated:
    transaction_id: UUID