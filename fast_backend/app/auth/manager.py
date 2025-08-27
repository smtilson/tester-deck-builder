from typing import Optional, Any

from beanie import PydanticObjectId
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.exceptions import UserAlreadyExists, UserNotExists
from fastapi_users.db import BeanieUserDatabase, ObjectIDIDMixin
import os
from datetime import datetime

from fast_backend.app.models import User, get_user_db
from fast_backend.app.schemas import UserCreate, UserUpdate, UserResponse, UserUpdatePermissions, UserListItem
from fast_backend.app.schemas import GameListItem
from fast_backend.app.core.exceptions import NotFoundException

SECRET = os.getenv("SECRET", "your-secret-key")



class UserManager(ObjectIDIDMixin, BaseUserManager[User, PydanticObjectId]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def create_from_dict(self, user_dict:dict[str, Any]):
        user = UserCreate(**user_dict)
        # this is happening because my UserCreate schema does not inherit from
        # BaseUserCreate. I don't because I don't want certain fields and want 
        # the API to be clean
        return await self.create(user)
    
    async def create(self, user_create: UserCreate) -> UserResponse:
        username = user_create.username
        exists = await User.find_one({"username": username})
        if exists is not None:
            raise UserAlreadyExists(f"A user with username: {username} already exists")
        user = await super().create(user_create=user_create)
        return UserResponse.model_validate(user)  # type: ignore
    
    async def update(self, user_update:UserUpdate) -> UserResponse:
        user = await self.get_model(user_update.id)
        updated_user = await super().update(user=user, user_update=user_update)
        updated_at = datetime.utcnow()
        updated_user.updated_at = updated_at
        updated_user = await updated_user.save()
        return UserResponse.model_validate(updated_user)
    
    async def delete(self, id: PydanticObjectId) -> bool:
        user = await self.get_model(id)
        await super().delete(user)
        return True

    async def _get_by_key(self, key: str, value: str) -> UserResponse:
        try:
            user = await User.find_one({key: value})
        except UserNotExists:
            raise UserNotExists(f"User with {key}: {value} does not exist")
        if not user:
            raise UserNotExists(f"User with {key}: {value} does not exist")
        return user

    async def get_by_username(self, username: str) -> UserResponse:
        user = await self._get_by_key("username", username)
        return UserResponse.model_validate(user)  # type: ignore

    async def get_by_email(self, email: str) -> UserResponse:
        user = await self._get_by_key("email", email)
        return UserResponse.model_validate(user)  # type: ignore

    async def get_list_item(self, user_id: PydanticObjectId) -> UserListItem:
        user = await self.get_model(user_id)
        return UserListItem.model_validate(user)  # type: ignore

    async def get_model(self, id: PydanticObjectId) -> User:
        try:
            # the BaseUserManager get method returns a model.
            user = await User.get(id)
        except UserNotExists:
            raise UserNotExists(f"User with ID: {id} does not exist")
        if not user:
            raise UserNotExists(f"User with ID: {id} does not exist")
        return user

    async def get_by_id(self, id: PydanticObjectId) -> UserResponse:
        user = await self._get_by_key("_id", id)
        return UserResponse.model_validate(user)  # type: ignore
    async def get(self, id: PydanticObjectId) -> UserResponse:
        user = await self.get_model(id)
        return UserResponse.model_validate(user)
    
    async def get_all(self) -> list[UserResponse]:
        users = await User.find().to_list()
        return [UserResponse.model_validate(user) for user in users]
    
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

