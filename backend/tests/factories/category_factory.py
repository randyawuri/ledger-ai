import factory

from app.categories.domain.models import (
    Category,
    TransactionType,
)

from tests.factories.user_factory import UserFactory


class CategoryFactory(factory.Factory):
    class Meta:
        model = Category

    user = factory.SubFactory(UserFactory)
    user_id = factory.SelfAttribute("user.id")

    name = "Food"

    transaction_type = TransactionType.DEBIT

    icon = "folder"

    color = "#4F46E5"