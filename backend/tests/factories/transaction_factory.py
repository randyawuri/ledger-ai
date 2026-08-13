from datetime import datetime, UTC

import factory

from app.transactions.domain.models import (
    Transaction,
    TransactionType,
)

from tests.factories.account_factory import AccountFactory
from tests.factories.category_factory import CategoryFactory


class TransactionFactory(factory.Factory):
    class Meta:
        model = Transaction

    account = factory.SubFactory(AccountFactory)
    account_id = factory.SelfAttribute("account.id")

    category = factory.SubFactory(CategoryFactory)
    category_id = factory.SelfAttribute("category.id")

    amount = 5000
    description = "Test transaction"
    merchant = "Test Merchant"

    transaction_type = TransactionType.DEBIT

    transaction_date = factory.LazyFunction(
        lambda: datetime.now(UTC)
    )