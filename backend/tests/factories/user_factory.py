import factory

from app.users.domain.models import User


class UserFactory(factory.Factory):
    class Meta:
        model = User

    email = factory.Sequence(
        lambda n: f"user{n}@example.com"
    )

    first_name = "John"

    last_name = "Doe"

    password_hash = "hashed_password"