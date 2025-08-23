# File: routers.py

# Import the necessary components from FastAPI and your application.
# You will need your FastAPIUsers instance, the authentication backend,
# and your user schemas (UserResponse, UserCreate, etc.).
from fastapi import APIRouter

from fast_backend.app.schemas.users import UserCreate, UserResponse, UserUpdate, UserLogin
from fast_backend.app.auth.backend import auth_backend
from fast_backend.app.auth.fast_api_users_instance import (
    fastapi_users,
    current_active_user,
)

# Create a master router for all authentication-related endpoints.
# This router will act as a container for all the sub-routers.
auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

# Include all the individual routers from fastapi-users into the master router.
# The `prefix` and `tags` you define on the master router will apply
# to all the included sub-routers, keeping your code DRY (Don't Repeat Yourself).
# Note that we are using `auth_router.include_router` instead of `app.include_router`.

# This router handles JWT authentication (login/logout).
auth_router.include_router(
    fastapi_users.get_auth_router(auth_backend, requires_verification=True),
    prefix="/jwt",
)

# This router handles user registration.
auth_router.include_router(
    fastapi_users.get_register_router(UserResponse, UserCreate),
)

# This router handles password reset requests.
auth_router.include_router(
    fastapi_users.get_reset_password_router(),
)

# This router handles user verification.
auth_router.include_router(
    fastapi_users.get_verify_router(UserResponse),
)
