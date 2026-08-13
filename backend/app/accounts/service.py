from decimal import Decimal

from sqlalchemy import func

from app.transactions.domain.models import (
    Transaction,
    TransactionType,
)

from sqlalchemy.orm import Session

from app.accounts.domain.models import Account


class AccountService:

    def __init__(self, db: Session):
        self.db = db

    def create_account(
        self,
        *,
        user_id,
        name,
        institution,
        currency,
        opening_balance,
    ):
        account = Account(
            user_id=user_id,
            name=name,
            institution=institution,
            currency=currency,
            opening_balance=opening_balance,
        )

        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)

        return account

    def get_accounts(self, user_id):
        return (
            self.db.query(Account)
            .filter(Account.user_id == user_id)
            .all()
        )
    
    def get_account_balance(
        self,
        user,
        account_id,
        ):
        account = (
        self.db.query(Account)
        .filter(
            Account.id == account_id,
            Account.user_id == user.id,
            )
        .first()
    )

        if account is None:
            return None

        income = (
            self.db.query(
            func.coalesce(func.sum(Transaction.amount), 0)
        )
        .filter(
            Transaction.account_id == account.id,
            Transaction.transaction_type == TransactionType.CREDIT,
        )
        .scalar()
    )

        expenses = (
            self.db.query(
            func.coalesce(func.sum(Transaction.amount), 0)
        )
        .filter(
            Transaction.account_id == account.id,
            Transaction.transaction_type == TransactionType.DEBIT,
        )
        .scalar()
    )

        current_balance = (
            Decimal(account.opening_balance)
            + Decimal(income)
            - Decimal(expenses)
            )

        return {
            "account_id": account.id,
            "opening_balance": Decimal(account.opening_balance),
            "total_income": Decimal(income),
            "total_expenses": Decimal(expenses),
            "current_balance": current_balance,
            }