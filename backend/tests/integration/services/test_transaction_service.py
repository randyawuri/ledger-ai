from decimal import Decimal
from datetime import datetime, UTC

from app.transactions.service import TransactionService
from app.transactions.schemas import TransactionCreate

from tests.factories.account_factory import AccountFactory
from tests.factories.category_factory import CategoryFactory


def test_create_transaction(db):
    account = AccountFactory()
    category = CategoryFactory(user=account.user)

    db.add(account.user)
    db.add(account)
    db.add(category)
    db.flush()

    service = TransactionService(db)

    payload = TransactionCreate(
        account_id=account.id,
        category_id=category.id,
        amount=Decimal("2500"),
        description="Lunch",
        merchant="Chicken Republic",
        transaction_type="debit",
        transaction_date=datetime.now(UTC),
    )

    transaction = service.create(
        payload,
        user_id=account.user.id,
    )

    assert transaction.id is not None
    assert transaction.amount == Decimal("2500")
    assert transaction.description == "Lunch"