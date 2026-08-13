from uuid import UUID

from sqlalchemy.orm import Session

from app.merchants.domain.models import Merchant


class MerchantRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, merchant: Merchant):
        self.db.add(merchant)
        return merchant

    def get(self, merchant_id: UUID):
        return (
            self.db.query(Merchant)
            .filter(Merchant.id == merchant_id)
            .first()
        )

    def get_by_name(self, name: str):
        return (
            self.db.query(Merchant)
            .filter(Merchant.name == name)
            .first()
        )

    def list(self):
        return (
            self.db.query(Merchant)
            .order_by(Merchant.name)
            .all()
        )

    def delete(self, merchant: Merchant):
        self.db.delete(merchant)