from dataclasses import dataclass
from uuid import UUID

from app.events.base import DomainEvent


@dataclass(slots=True)
class TransactionCreated(DomainEvent):

    transaction_id: UUID