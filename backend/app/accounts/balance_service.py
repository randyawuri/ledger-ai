from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.accounts.domain.models import Account
from app.transactions.domain.models import (
    Transaction,
    TransactionType,
)


class BalanceService:

    def __init__(self, db: Session):
        self.db = db

    def calculate(self, account_id):

        account = (
            self.db.query(Account)
            .filter(Account.id == account_id)
            .first()
        )

        credits = (
            self.db.query(func.coalesce(func.sum(Transaction.amount), 0))
            .filter(
                Transaction.account_id == account_id,
                Transaction.transaction_type == TransactionType.CREDIT,
            )
            .scalar()
        )

        debits = (
            self.db.query(func.coalesce(func.sum(Transaction.amount), 0))
            .filter(
                Transaction.account_id == account_id,
                Transaction.transaction_type == TransactionType.DEBIT,
            )
            .scalar()
        )

        return account.opening_balance + credits - debits