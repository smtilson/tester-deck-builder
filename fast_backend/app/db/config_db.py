from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from fastapi import FastAPI

from fast_backend.app.core.config_app import settings
from fast_backend.app.models import User, Deck, DeckCard, Card, Game
from fast_backend.app.api.endpoints.test import TestDocument
DOCUMENT_MODELS=[User, Deck, Card, Game, TestDocument]
PATHS = MODEL_PATHS + AERICH_PATH



async def init_db():
    """Initializes the database connection."""
    client = AsyncIOMotorClient(settings.DATABASE_URI)
    await init_beanie(database=client[settings.DATABASE_NAME], document_models=DOCUMENT_MODELS)
    return client

async def close_db(client):
    """Closes the database connection."""
    await client.close()