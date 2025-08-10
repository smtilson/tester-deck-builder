# app/db/user_db.py
from typing import AsyncGenerator
from fastapi_users_tortoise import TortoiseUserDatabase
from fast_backend.app.models.users import User  # Import your User ORM model


async def get_user_db() -> AsyncGenerator[TortoiseUserDatabase, None]:
    """
    FastAPI dependency that yields a TortoiseUserDatabase instance.
    This adapts your Tortoise User model for fastapi-users.
    """
    yield TortoiseUserDatabase(user_model=User)
