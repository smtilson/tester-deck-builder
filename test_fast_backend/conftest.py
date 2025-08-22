# conftest.py
import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

# import the models you want available in tests
from fast_backend.app.db.config_db import DOCUMENT_MODELS


@pytest_asyncio.fixture
async def db_client():
    """
    Initialize Beanie once per test session.
    """
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["test_db"]
    # IMPORTANT: register your models here
    await init_beanie(database=db, document_models=DOCUMENT_MODELS)

    for name in await db.list_collection_names():
        await db.drop_collection(name)

    yield db

    # cleanup after test
    await client.drop_database("test_db")
    client.close()

@pytest_asyncio.fixture
async def clean_db(db_client):
    for name in await db_client.list_collection_names():
        await db_client.drop_collection(name)
    yield
