import os
import uuid
from fastapi_users import models, FastAPIUsers
from fastapi_users.authentication import (
    JWTStrategy,
    BearerTransport,
    AuthenticationBackend,
)
from fast_backend.app.auth.manager import get_user_manager
from fast_backend.app.models.users import User

JWT_SECRET = os.getenv("SECRET_KEY", "your-secret-key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy[models.UP, models.ID]:
    return JWTStrategy(secret=JWT_SECRET, lifetime_seconds=3000)


auth_backend = AuthenticationBackend(
    name="jwt", transport=bearer_transport, get_strategy=get_jwt_strategy
)
# moved to the fast_api_users_instance file
# fastapi_users = FastAPIUsers[User, uuid.uuid4](get_user_manager, [auth_backend])
# current_active_user = fastapi_users.current_user(active=True)

