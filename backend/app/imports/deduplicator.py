from sqlalchemy import select
from sqlalchemy.orm import Session

from app.transactions.domain.models import Transaction


class DuplicateDetector:

    def __init__(self, db: Session):
        self.db = db

    def exists(
        self,
        account_id,
        row,
    ) -> bool:

        stmt = (
            select(Transaction.id)
            .where(
                Transaction.account_id == account_id,
                Transaction.amount == row.amount,
                Transaction.description == row.description,
                Transaction.transaction_date == row.transaction_date,
            )
        )

        return self.db.scalar(stmt) is not None