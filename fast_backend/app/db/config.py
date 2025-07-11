from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from tortoise import Tortoise

from app.core.config import settings


MODEL_PATHS = [
    "app.models.users",
    "app.models.decks",
    "app.models.deck_cards",
    "app.models.cards",
]

AERICH_PATH = ["aerich.models"]

PATHS = MODEL_PATHS + AERICH_PATH

TORTOISE_ORM = {
    "connections": {"default": settings.DATABASE_URI},
    "apps": {
        "models": {
            "models": PATHS,
            "default_connection": "default",
        },
    },
}


async def init_db():
    """Initializes the database connection."""
    await Tortoise.init(db_url=settings.DATABASE_URI, modules={"models": MODEL_PATHS})
    await Tortoise.generate_schemas()


async def close_db():
    """Close the database connection."""
    await Tortoise.close_connections()


def register_db(app: FastAPI) -> None:
    register_tortoise(
        app,
        config=TORTOISE_ORM,
        generate_schemas=True,
        add_exception_handlers=True,
    )
