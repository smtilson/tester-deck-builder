from __future__ import annotations
from typing import Optional
from uuid import UUID
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, InvalidPasswordException, UUIDIDMixin
from fastapi_users.exceptions import UserAlreadyExists
from fastapi_users_tortoise import TortoiseUserDatabase
from fastapi_users.password import PasswordHelper
from passlib.context import CryptContext
from ..schemas.users import UserCreate, UserUpdate

from ..core.config import Environment, settings
from ..services.email import render_email_template
from ..services.worker import queue


from ..models.users import User
from ..db.users_db import get_user_db


context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")
password_helper = PasswordHelper(context)


class UserManager(UUIDIDMixin, BaseUserManager[User, UUID]):

    reset_password_token_secret = settings.SECRET_KEY
    verification_token_secret = settings.SECRET_KEY
    
    async def create(self, user_create: UserCreate, safe: bool=False, request: Optional[Request]=None) -> User:
        """Override to add custom user creation logic."""
        print("custom create called")
        existing_username_user = await User.get_or_none(username=user_create.username)
        if existing_username_user is not None:
            raise UserAlreadyExists()
            
        
        return await super().create(user_create=user_create, safe=safe, request=request)
        
    async def on_after_register(
        self, user: User, request: Request | None = None
    ) -> None:
        name = user.name
        subject = f"Welcome to {name}!" if name else "Welcome!"
        print(subject)
        await queue.enqueue(
            "send_email_task",
            recipient=(user.email, None),
            subject=subject,
            html=render_email_template("welcome.html", context={"user": user}),
        )

    async def validate_password(self, password: str, user: User) -> None:
        conditions = {}
        if settings.ENVIRONMENT == Environment.prod:
            conditions = {
                "Password should be at least 8 characters": len(password) < 8,
                "Password should not contain e-mail": user.email in password,
                "Password should contain at least one number or special characters(@*)": password.isalpha(),
                "Password should not contain only numeric values": password.isnumeric(),
            }
        for msg, condition in conditions.items():
            if condition:
                raise InvalidPasswordException(msg)


async def get_user_manager(user_db: TortoiseUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db, password_helper)
