import pytest
import sys
import os
from pathlib import Path
from tortoise import Tortoise
from tortoise.contrib.test import finalizer, initializer

#from fast_backend.app.db.config_db import MODEL_PATHS
from test_fast_backend.sample_data import *


PROJECT_ROOT = Path(__file__).resolve().parent.parent # Adjust based on your conftest location
sys.path.insert(0, str(PROJECT_ROOT)) # Insert at the beginning for highest priority

MODEL_PATHS = [
    #"fast_backend.app.models.users",
    #"fast_backend.app.models.decks",
    #"fast_backend.app.models.deck_cards",
    "fast_backend.app.models.cards",
]

# Use a session-scoped fixture to initialize the database once for all tests.
@pytest.fixture(scope="session")
async def old_init_db():
    """
    Initializes and tears down the database connection for the entire test session.
    """
    print("init_db fixture called")
    TEST_DB_URL = "sqlite://:memory:"
    await Tortoise.init(db_url=TEST_DB_URL, modules={"models": MODEL_PATHS})
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


@pytest.fixture(scope="session")
async def init_db():
    """
    Initializes and tears down the database connection for the entire test session.
    """
    print("init_db fixture called")

    initializer(MODEL_PATHS,db_url="sqlite://:memory:", app_label="cards")
    yield
    finalizer()
    


# Use an autouse fixture to ensure the db_connection is always set up.
# This fixture also handles cleanup between individual tests.
# @pytest.fixture(autouse=True)
async def db(init_db):
    """
    Clears the database between each test function.
    """
    yield
    # This will clear all tables after each test. If you need to preserve some data, adjust accordingly.
    await Tortoise._drop_databases()


# The client fixture is currently a placeholder. Implement it when you need to test FastAPI endpoints.
@pytest.fixture
async def client():
    """
    HTTP client for endpoint tests (works later when testing FastAPI routes).
    """
    # async with AsyncClient(app=app, base_url="http://test") as ac:
    #     yield ac
    pass  # TODO: Import and use the FastAPI app when needed
