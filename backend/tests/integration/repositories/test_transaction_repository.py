from decimal import Decimal

from app.transactions.repository import TransactionRepository

from tests.factories.account_factory import AccountFactory
from tests.factories.transaction_factory import TransactionFactory


def test_create_transaction(db):

    repository = TransactionRepository(db)

    transaction = TransactionFactory()

    repository.create(transaction)

    db.flush()

    assert transaction.id is not None


def test_get_transaction(db):

    repository = TransactionRepository(db)

    transaction = TransactionFactory()

    repository.create(transaction)

    db.flush()

    loaded = repository.get(transaction.id)

    assert loaded.id == transaction.id


def test_list_transactions(db):

    repository = TransactionRepository(db)

    account = AccountFactory()

    tx1 = TransactionFactory(account=account)
    tx2 = TransactionFactory(account=account)

    other_account = AccountFactory()

    tx3 = TransactionFactory(account=other_account)

    repository.create(tx1)
    repository.create(tx2)
    repository.create(tx3)

    db.flush()

    rows = repository.list_by_account(account.id)

    assert len(rows) == 2


def test_delete_transaction(db):

    repository = TransactionRepository(db)

    transaction = TransactionFactory()

    repository.create(transaction)

    db.flush()

    repository.delete(transaction)

    db.flush()

    assert repository.get(transaction.id) is None


def test_update_transaction(db):
    repository = TransactionRepository(db)

    transaction = TransactionFactory(
        description="Original description",
        amount="1000.00",
    )

    repository.create(transaction)
    db.flush()

    transaction.description = "Updated description"
    transaction.amount = "2500.00"

    updated = repository.update(transaction)

    assert updated.description == "Updated description"
    assert updated.amount == Decimal("2500.00")