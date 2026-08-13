import factory

from app.accounts.domain.models import Account
from tests.factories.user_factory import UserFactory


class AccountFactory(factory.Factory):
    class Meta:
        model = Account

    user = factory.SubFactory(UserFactory)

    user_id = factory.SelfAttribute("user.id")

    name = "Checking"

    institution = "GTBank"

    currency = "NGN"

    opening_balance = 100000