from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from fastapi import FastAPI

from fast_backend.app.core.config_app import settings
from fast_backend.app.models import User, Deck, DeckCard, Card, Game
from fast_backend.app.models.test import TestDocument

DOCUMENT_MODELS=[User, Deck, Card, Game, TestDocument]

async def init_db():
    """Initializes the database connection."""
    client = AsyncIOMotorClient(settings.DATABASE_URI)
    await init_beanie(database=client[settings.DATABASE_NAME], document_models=DOCUMENT_MODELS)
    return client

async def close_db(client: AsyncIOMotorClient):
    """Closes the database connection."""
    client.close()
    return None

async def drop_db(client: AsyncIOMotorClient):
    """
    Drops all collections defined in DOCUMENT_MODELS.
    Use with caution, as this will delete all data.
    """
    client = AsyncIOMotorClient(settings.DATABASE_URI)
    db = client[settings.DATABASE_NAME]
    for model in DOCUMENT_MODELS:
        print(f"Dropping collection: {model.Settings.name}")
        await db[model.Settings.name].drop()
    print("Database collections dropped successfully!")