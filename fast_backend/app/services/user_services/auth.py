import os
from uuid import UUID
from fastapi_users import models, FastAPIUsers
from fastapi_users.authentication import (
    JWTStrategy,
    BearerTransport,
    AuthenticationBackend,
)
from fastapi_users_tortoise.access_token import (
    TortoiseBaseAccessTokenModel,
    TortoiseAccessTokenDatabase,
)
from .manager import get_user_manager
from ...models.users import User

JWT_SECRET = os.getenv("SECRET_KEY", "your-secret-key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy[models.UP, models.ID]:
    return JWTStrategy(secret=JWT_SECRET, lifetime_seconds=3000)


auth_backend = AuthenticationBackend(
    name="jwt", transport=bearer_transport, get_strategy=get_jwt_strategy
)

fastapi_users = FastAPIUsers[User, UUID](get_user_manager, [auth_backend])
current_active_user = fastapi_users.current_user(active=True)


"""
class AccessToken(TortoiseBaseAccessTokenModel):
    pass


async def get_access_token_db():
    yield TortoiseAccessTokenDatabase[AccessToken](AccessToken)
"""
