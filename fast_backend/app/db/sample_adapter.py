from fast_backend.app.models.users import User as UserORM



# from fastapi_users.password import get_password_hash
from fast_backend.app.schemas.users import *
import asyncio
import uuid


user_data = {
    "username": "sample",
    "password": "samplepass",
    "email": "sample@example.com",
}

TORTOISE_CONFIG = {
    "connections": {"default": "sqlite://:memory:"},
    "apps": {
        "models": {
            "models": ["fast_backend.app.models.users"],  # Path to your user model
            "default_connection": "default",
        }
    },
}


async def tinker_with_db():
    print("Initializing Tortoise ORM...")
    #await Tortoise.init(config=TORTOISE_CONFIG)
    print("Generating schemas...")
    #await Tortoise.generate_schemas()
    print("Database ready!")

    # Instantiate the TortoiseUserDatabase adapter
    #adapter = TortoiseUserDatabase(UserORM)
    print(f"TortoiseUserDatabase adapter created: {adapter}")
