from uuid import UUID

from sqlalchemy import select

from app.accounts.domain.models import Account
from app.db.repositories import BaseRepository


class AccountRepository(BaseRepository):

    def create(
        self,
        account: Account,
    ) -> Account:

        return self.save(account)

    def get_by_id(
        self,
        account_id: UUID,
    ) -> Account | None:

        return self.db.get(
            Account,
            account_id,
        )

    def list_by_user(
        self,
        user_id: UUID,
    ):

        stmt = (
            select(Account)
            .where(Account.user_id == user_id)
            .order_by(Account.name)
        )

        return self.db.scalars(stmt).all()

    def update(
        self,
        account: Account,
    ) -> Account:

        self.flush()
        self.refresh(account)

        return account

    def delete(
        self,
        account: Account,
    ):

        self.delete_entity(account)