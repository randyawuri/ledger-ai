from dataclasses import dataclass

from app.transactions.domain.models import Transaction


@dataclass
class TransactionCreated:

    transaction: Transaction