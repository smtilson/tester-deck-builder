from factory import Factory

from ...models.users import User


class UserFactory(Factory):
    class Meta:
        model = User
