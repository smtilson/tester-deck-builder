from typing import Optional, Any

from beanie import PydanticObjectId
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import BeanieUserDatabase, ObjectIDIDMixin
import os

from fast_backend.app.models.users import User, get_user_db
from fast_backend.app.schemas.users import UserCreate, UserUpdate, UserResponse, UserUpdatePermissions
from fast_backend.app.schemas.games import GameListItem

SECRET = os.getenv("SECRET", "your-secret-key")


class UserManager(ObjectIDIDMixin, BaseUserManager[User, PydanticObjectId]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def validate_password(self, password: str, user: UserCreate | User) -> None:
        # this is to determine if the password is strong enough
        return await super().validate_password(password, user)
    
    async def on_after_register(self, user: User, request: Optional[Request] = None):
        # send welcome email?
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        # send email to recover pw?
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        # send email to verify email address?
        print(f"Verification requested for user {user.id}. Verification token: {token}")


    async def update_permissions(self, user: User, permission_data: UserUpdatePermissions) -> User:
        update_data = permission_data.model_dump(exclude_unset=True)
        set_updates : dict[str,bool]={}
        add_to_set_updates : dict[str,dict[str,list[GameListItem]]]={}
        for key, value in update_data.items():
            if isinstance(value, bool):
                set_updates[key] = value
            elif isinstance(value, list):
                add_to_set_updates[key] = {"$each": value}
        update_query = {}
        if set_updates:
            update_query["$set"] = set_updates
        if add_to_set_updates:
            update_query["$addToSet"] = add_to_set_updates
        if update_query:
            await user.update(update_query)
            await user.reload()
        await UserManager.update_user(user.id, update_query)
        return user

async def get_user_manager(user_db: BeanieUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)
