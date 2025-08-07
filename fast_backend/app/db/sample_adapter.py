from .users_db import get_user_db, MyTortoiseUserDatabase
from ..models.users import User as UserORM
from fastapi_users_tortoise import TortoiseUserDatabase
from tortoise import Tortoise, run_async
from tortoise.models import Model
#from fastapi_users.password import get_password_hash
from fastapi_users_tortoise import TortoiseUserDatabase
from ..schemas.users import *
import asyncio
from uuid import UUID




user_data = {"username":"sample", "password":"samplepass", "email":"sample@example.com"}

TORTOISE_CONFIG = {
    "connections": {"default": "sqlite://:memory:"},
    "apps": {
        "models": {
            "models": ["fast_backend.app.models.users"], # Path to your user model
            "default_connection": "default",
        }
    }
}

async def tinker_with_db():
    print("Initializing Tortoise ORM...")
    await Tortoise.init(config=TORTOISE_CONFIG)
    print("Generating schemas...")
    await Tortoise.generate_schemas()
    print("Database ready!")

    # Instantiate the TortoiseUserDatabase adapter
    adapter = TortoiseUserDatabase(UserORM)
    print(f"TortoiseUserDatabase adapter created: {adapter}")
