# app/auth/fastapi_users_instance.py
from beanie.odm.fields import PydanticObjectId
from fastapi_users import FastAPIUsers
from fast_backend.app.auth.backend import auth_backend
from fast_backend.app.models import get_user_db
from fast_backend.app.auth.manager import get_user_manager
from fast_backend.app.schemas import UserResponse


# Instantiate FastAPIUsers
# user_db_dependency: A dependency that provides the user database adapter
# auth_backends: A list of authentication backends you want to support

fastapi_users = FastAPIUsers[UserResponse, PydanticObjectId](
    get_user_manager=get_user_manager,
    auth_backends=[auth_backend],
)

current_active_user = fastapi_users.current_user(active=True)
