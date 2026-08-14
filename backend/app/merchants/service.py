from sqlalchemy import func
from sqlalchemy.orm import Session

from app.accounts.domain.models import Account
from app.merchants.domain.models import Merchant
from app.merchants.normalizer import MerchantNormalizer
from app.merchants.repository import MerchantRepository
from app.transactions.domain.models import Transaction, TransactionType

class MerchantService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = MerchantRepository(db)
        self.normalizer = MerchantNormalizer()

    def resolve(
        self,
        merchant: str | None,
        description: str,
    ) -> Merchant:
        name = self.normalizer.normalize(
            merchant=merchant,
            description=description,
        )

        existing = self.repository.get_by_name(name)

        if existing:
            return existing

        merchant_obj = Merchant(name=name)
        return self.repository.create(merchant_obj)

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