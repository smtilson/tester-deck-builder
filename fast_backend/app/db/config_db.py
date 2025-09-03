from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from fastapi import FastAPI

from fast_backend.app.core.config_app import settings
from fast_backend.app.models import User, Deck, DeckCard, Card, Game, BaseDocument
from fast_backend.app.models.test import TestDocument

DOCUMENT_MODELS=[User, Deck, Card, Game]

async def init_db():
    """Initializes the database connection."""
    client = AsyncIOMotorClient(settings.DATABASE_URI, uuidRepresentation="standard")
    db = client[settings.DATABASE_NAME]
    await init_beanie(database=db, document_models=DOCUMENT_MODELS)
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
    await client.drop_database(settings.DATABASE_NAME)
    for model in DOCUMENT_MODELS:
        all_docs = await model.find_all().to_list()
        if len(all_docs) != 0:
            print(all_docs)
            raise Exception(f"{model.Settings.name} table not successfully dropped.")
        
    print("Database collections dropped successfully!")