from contextlib import asynccontextmanager

from fast_backend.app.auth.manager import get_user_manager
from fast_backend.app.models import User
from fast_backend.app.db.users_db import get_user_db
from fast_backend.app.models import UserCreate

get_user_db_context = asynccontextmanager(get_user_db)
get_user_manager_context = asynccontextmanager(get_user_manager)


async def create_user(user_in: UserCreate) -> User:
    """This function is used to create user outside of views"""

    async with get_user_db_context() as user_db:
        async with get_user_manager_context(user_db) as user_manager:
            return await user_manager.create(user_in)
