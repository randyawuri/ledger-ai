from sqlalchemy import func
from sqlalchemy.orm import Session

from app.accounts.domain.models import Account
from app.transactions.domain.models import Transaction
from app.transactions.domain.models import TransactionType


class MerchantService:

    def __init__(self, db: Session):
        self.db = db

    def spending(self, user):

        rows = (
            self.db.query(
                Transaction.merchant,
                func.sum(Transaction.amount).label("total"),
                func.count(Transaction.id).label("count"),
            )
            .join(Account)
            .filter(
                Account.user_id == user.id,
                Transaction.transaction_type == TransactionType.DEBIT,
            )
            .group_by(Transaction.merchant)
            .order_by(func.sum(Transaction.amount).desc())
            .all()
        )

        return [
            {
                "merchant": row.merchant,
                "total_spent": row.total,
                "transactions": row.count,
            }
            for row in rows
        ]