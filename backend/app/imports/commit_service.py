from sqlalchemy.orm import Session

from app.imports.deduplicator import DuplicateDetector
from app.imports.schemas import ImportedTransaction
from app.transactions.service import TransactionService


class CommitService:
    """
    Persists imported transactions.
    """

    def __init__(self, db: Session):
        self.db = db
        self.transaction_service = TransactionService(db)
        self.duplicate_detector = DuplicateDetector(db)

    def commit(
        self,
        account_id,
        rows: list[ImportedTransaction],
    ):

        imported = []

        for row in rows:

            if self.duplicate_detector.exists(
                account_id,
                row,
            ):
                continue

            tx = self.transaction_service.create_transaction(
                account_id=account_id,
                category_id=None,
                transaction_type=row.transaction_type,
                amount=row.amount,
                description=row.description,
                merchant=row.merchant,
                transaction_date=row.transaction_date,
            )

            imported.append(tx)

        return imported