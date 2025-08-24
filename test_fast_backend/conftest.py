# conftest.py
import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from fastapi_users.db import BeanieUserDatabase

# import the models you want available in tests
from fast_backend.app.auth.manager import UserManager, get_user_manager
from fast_backend.app.models.users import get_user_db
from fast_backend.app.db.config_db import DOCUMENT_MODELS
from .sample_data import all_test_data


@pytest_asyncio.fixture
async def init_db():
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

# Assuming you already have a fixture for database initialization called 'init_db'
# and that 'get_user_db' depends on it indirectly.

@pytest_asyncio.fixture(scope="function")
async def user_db(init_db) -> BeanieUserDatabase:
    """Fixture to get the BeanieUserDatabase instance."""
    # The get_user_db function is a generator, so we use 'anext' or manual iteration
    # to get the yielded value.
    db_generator = get_user_db()
    # Use 'await anext(db_generator)' for simple extraction in recent Python versions
    # or handle the generator manually:
    try:
        user_db_instance = await anext(db_generator)
    except StopAsyncIteration:
        # Should not happen in this case, but good practice
        raise Exception("get_user_db yielded no database instance.")
        
    yield user_db_instance
    
    # Optional: Clean up after the test if your DB needs explicit closing
    await db_generator.aclose()
    
    


@pytest_asyncio.fixture(scope="function")
async def user_manager(user_db: BeanieUserDatabase) -> UserManager:
    """Fixture to get the UserManager instance."""
    # Replicate the logic of get_user_manager: yield UserManager(user_db)
    manager_generator = get_user_manager(user_db=user_db)
    
    try:
        manager_instance = await anext(manager_generator)
    except StopAsyncIteration:
        raise Exception("get_user_manager yielded no manager instance.")

    # Yield the manager instance for the tests to use
    yield manager_instance
    
    # Optional: Clean up if the manager needs it
    await manager_generator.aclose()

# Note: You need to import the async generator helper function if not using Python 3.10+
async def anext(agen):
    """Helper for extracting value from async generator."""
    try:
        return await agen.__anext__()
    except AttributeError:
        # Fallback for Python < 3.10 if anext is not built-in
        return await agen.asend(None)