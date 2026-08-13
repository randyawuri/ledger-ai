from uuid import UUID
from warnings import filters

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.accounts.domain.models import Account
from app.automation.service import AutomationService
from app.transactions.domain.models import Transaction
from app.transactions.repository import TransactionRepository
from app.transactions.schemas import (
    TransactionCreate,
    TransactionUpdate,
)
from tests.fixtures import transactions


class TransactionService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = TransactionRepository(db)

    def create(
        self,
        payload: TransactionCreate,
        user_id: UUID,
    ) -> Transaction:
        """
        Create a transaction only if the account belongs
        to the authenticated user.
        """

        account = (
            self.db.query(Account)
            .filter(
                Account.id == payload.account_id,
                Account.user_id == user_id,
            )
            .first()
        )

        if account is None:
            raise ValueError("Account not found")

        transaction = Transaction(
            account_id=payload.account_id,
            category_id=payload.category_id,
            transaction_type=payload.transaction_type,
            amount=payload.amount,
            description=payload.description,
            merchant=payload.merchant,
            transaction_date=payload.transaction_date,
        )

        self.repository.create(transaction)

        AutomationService(self.db).process_transaction(transaction)

        return transaction

    def get_transaction(
            self,
            transaction_id: UUID,
            user_id: UUID,
    ):
        return self.repository.get_for_user(
            transaction_id,
            user_id,
        )
    
    def search_transactions(
            self,
            user,
            filters,
            *,
            limit: int = 50,
            offset: int = 0,
    ):
        query = (
            self.db.query(Transaction)
            .join(Account)
            .filter(Account.user_id == user.id)
        )

        if filters.account_id:
            query = query.filter(
                Transaction.account_id == filters.account_id
            )

        if filters.category_id:
            query = query.filter(
                Transaction.category_id == filters.category_id
            )

        if filters.transaction_type:
            query = query.filter(
                Transaction.transaction_type == filters.transaction_type
            )

        if filters.start_date:
            query = query.filter(
                func.date(Transaction.transaction_date)
                >= filters.start_date
            )
        if filters.end_date:
            query = query.filter(
                func.date(Transaction.transaction_date)
                <= filters.end_date
            )
        if filters.min_amount is not None:
            query = query.filter(
                Transaction.amount >= filters.min_amount
            )

        if filters.max_amount is not None:
            query = query.filter(
                Transaction.amount <= filters.max_amount
            )

        if filters.merchant:
            query = query.filter(
                Transaction.merchant.ilike(
                    f"%{filters.merchant}%"
                )
            )

        if filters.description:
            query = query.filter(
                Transaction.description.ilike(
                    f"%{filters.description}%"
                )
            )
        total = query.count()

        transactions = (
            query
            .order_by(
                Transaction.transaction_date.desc()
            )
            .limit(limit)
            .offset(offset)
            .all()
        )

        return {
            "items": transactions,
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    

    def get_transaction_for_user(
            self,
            transaction_id: UUID,
            user_id: UUID,
    ) -> Transaction | None:
        return self.repository.get_for_user(
            transaction_id=transaction_id,
            user_id=user_id,
        )

    def update_transaction(
            self,
            transaction_id: UUID,
            user_id: UUID,
            payload: TransactionUpdate,
    ) -> Transaction | None:
        transaction = self.repository.get_for_user(
            transaction_id=transaction_id,
            user_id=user_id,
        )
        
        if transaction is None:
            return None
        
        updates = payload.model_dump(exclude_unset=True)
        
        for field, value in updates.items():
            setattr(transaction, field, value)
            
        return self.repository.update(transaction)