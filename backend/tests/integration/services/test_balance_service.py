from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from app.accounts.balance_service import BalanceService
from app.accounts.domain.models import Account
from app.transactions.domain.models import Transaction, TransactionType
from tests.factories.user_factory import UserFactory


def create_account(db, opening_balance="100000.00"):
    user = UserFactory()

    db.add(user)
    db.flush()

    account = Account(
        user_id=user.id,
        name="Checking",
        institution="GTBank",
        currency="NGN",
        opening_balance=Decimal(opening_balance),
    )

    db.add(account)
    db.flush()

    return account


def create_transaction(
    db,
    account,
    transaction_type,
    amount,
):
    transaction = Transaction(
        account_id=account.id,
        transaction_type=transaction_type,
        amount=Decimal(amount),
        description="Test transaction",
        transaction_date=datetime.now(UTC),
    )

    db.add(transaction)
    db.flush()

    return transaction


def test_balance_returns_opening_balance_when_no_transactions(db):
    account = create_account(db, "100000.00")

    balance = BalanceService(db).calculate(account.id)

    assert balance == Decimal("100000.00")


def test_balance_adds_credits(db):
    account = create_account(db, "100000.00")

    create_transaction(
        db,
        account,
        TransactionType.CREDIT,
        "50000.00",
    )

    balance = BalanceService(db).calculate(account.id)

    assert balance == Decimal("150000.00")


def test_balance_subtracts_debits(db):
    account = create_account(db, "100000.00")

    create_transaction(
        db,
        account,
        TransactionType.DEBIT,
        "20000.00",
    )

    balance = BalanceService(db).calculate(account.id)

    assert balance == Decimal("80000.00")


def test_balance_handles_multiple_transactions(db):
    account = create_account(db, "100000.00")

    create_transaction(
        db,
        account,
        TransactionType.CREDIT,
        "50000.00",
    )

    create_transaction(
        db,
        account,
        TransactionType.DEBIT,
        "20000.00",
    )

    create_transaction(
        db,
        account,
        TransactionType.DEBIT,
        "10000.00",
    )

    balance = BalanceService(db).calculate(account.id)

    assert balance == Decimal("120000.00")


def test_balance_changes_when_transaction_amount_changes(db):
    account = create_account(db, "100000.00")

    transaction = create_transaction(
        db,
        account,
        TransactionType.DEBIT,
        "20000.00",
    )

    assert BalanceService(db).calculate(account.id) == Decimal("80000.00")

    transaction.amount = Decimal("5000.00")
    db.flush()

    assert BalanceService(db).calculate(account.id) == Decimal("95000.00")


def test_balance_changes_when_transaction_type_changes(db):
    account = create_account(db, "100000.00")

    transaction = create_transaction(
        db,
        account,
        TransactionType.DEBIT,
        "20000.00",
    )

    assert BalanceService(db).calculate(account.id) == Decimal("80000.00")

    transaction.transaction_type = TransactionType.CREDIT
    db.flush()

    assert BalanceService(db).calculate(account.id) == Decimal("120000.00")


def test_balance_rejects_unknown_account(db):

    with pytest.raises(ValueError, match="Account not found"):
        BalanceService(db).calculate(uuid4())