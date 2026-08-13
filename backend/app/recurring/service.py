from sqlalchemy.orm import Session

from app.accounts.domain.models import Account
from app.recurring.detector import RecurringDetector
from app.transactions.domain.models import Transaction
from app.transactions.domain.models import TransactionType


class RecurringService:

    def __init__(self, db: Session):
        self.db = db
        self.detector = RecurringDetector()

    def recurring_transactions(self, user):

        transactions = (
            self.db.query(Transaction)
            .join(
                Account,
                Transaction.account_id == Account.id,
            )
            .filter(
                Account.user_id == user.id,
                Transaction.transaction_type == TransactionType.DEBIT,
            )
            .order_by(
                Transaction.transaction_date.asc()
            )
            .all()
        )

        return self.detector.detect(transactions)