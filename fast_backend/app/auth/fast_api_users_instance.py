# app/auth/fastapi_users_instance.py
import uuid
from fastapi_users import FastAPIUsers
from fast_backend.app.auth.backend import (
    auth_backend,
)  # Import your authentication backend
from fast_backend.app.db.users_db import (
    get_user_db,
)  # Import your user database adapter
from fast_backend.app.schemas.users import (
    UserResponse,
    UserCreate,
    UserUpdate,
)  # Import your Pydantic schemas


# Instantiate FastAPIUsers
# user_db_dependency: A dependency that provides the user database adapter
# auth_backends: A list of authentication backends you want to support
# user_read_schema: Pydantic schema for user output
# user_create_schema: Pydantic schema for user creation input
# user_update_schema: Pydantic schema for user update input
fastapi_users = FastAPIUsers[UserResponse, uuid.UUID](
    get_user_db,
    [auth_backend],
    # UserResponse,
    # UserCreate,
    # UserUpdate,
)

current_active_user = fastapi_users.current_user(active=True)
