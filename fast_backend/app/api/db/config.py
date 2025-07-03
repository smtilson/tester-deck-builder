from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from app.core.config import settings


MODEL_PATHS = [
    "app.api.models.users",
    "app.api.models.decks",
    "app.api.models.cards",
    "aerich.models",
]

TORTOISE_ORM = {
    "connections": {"default": settings.DATABASE_URI},
    "apps": {
        "models": {
            "models": MODEL_PATHS,
            "default_connection": "default",
        },
    },
}


def register_db(app: FastAPI) -> None:
    register_tortoise(
        app,
        config=TORTOISE_ORM,
        generate_schemas=True,
        add_exception_handlers=True,
    )
