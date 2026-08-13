from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from app.accounts.domain.models import Account
from app.db.repositories import BaseRepository
from app.goals.domain.contribution import GoalContribution
from app.transactions.domain.models import Transaction


class TransactionRepository(BaseRepository):

    def create(
        self,
        transaction: Transaction,
    ) -> Transaction:
        self.db.add(transaction)
        self.db.flush()
        self.db.refresh(transaction)
        return transaction

    def get(
        self,
        transaction_id: UUID,
    ) -> Transaction | None:
        return self.db.get(
            Transaction,
            transaction_id,
        )

    def get_for_user(
        self,
        transaction_id: UUID,
        user_id: UUID,
    ) -> Transaction | None:
        stmt = (
            select(Transaction)
            .join(Transaction.account)
            .where(
                Transaction.id == transaction_id,
                Account.user_id == user_id,
            )
        )

        return self.db.scalar(stmt)

    def list_by_account(
        self,
        account_id: UUID,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Transaction]:
        stmt = (
            select(Transaction)
            .where(
                Transaction.account_id == account_id,
            )
            .order_by(
                Transaction.transaction_date.desc(),
            )
            .limit(limit)
            .offset(offset)
        )

        return self.db.scalars(stmt).all()

    def list_by_user(
        self,
        user_id: UUID,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Transaction]:
        stmt = (
            select(Transaction)
            .join(Transaction.account)
            .where(
                Account.user_id == user_id,
            )
            .order_by(
                Transaction.transaction_date.desc(),
            )
            .limit(limit)
            .offset(offset)
        )

        return self.db.scalars(stmt).all()

    def get_with_relationships_for_user(
        self,
        transaction_id: UUID,
        user_id: UUID,
    ) -> Transaction | None:
        stmt = (
            select(Transaction)
            .options(
                joinedload(Transaction.account),
                joinedload(Transaction.category),
                joinedload(Transaction.merchant_obj),
            )
            .join(Transaction.account)
            .where(
                Transaction.id == transaction_id,
                Account.user_id == user_id,
            )
        )

        return self.db.scalar(stmt)

    def update(
        self,
        transaction: Transaction,
    ) -> Transaction:
        self.db.flush()
        self.db.refresh(transaction)
        return transaction

    def delete(
        self,
        transaction: Transaction,
    ) -> None:
        self.db.delete(transaction)

    def count_by_user(
        self,
        user_id: UUID,
    ) -> int:
        stmt = (
            select(func.count())
            .select_from(Transaction)
            .join(Transaction.account)
            .where(
                Account.user_id == user_id,
            )
        )

        return self.db.scalar(stmt) or 0

    def get_contribution_by_transaction(
        self,
        transaction_id: UUID,
    ) -> GoalContribution | None:
        return (
            self.db.query(GoalContribution)
            .filter(
                GoalContribution.transaction_id == transaction_id,
            )
            .first()
        )