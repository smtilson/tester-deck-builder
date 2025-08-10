# conftest.py
import pytest
from tortoise import Tortoise
from httpx import AsyncClient
from fast_backend.app.main import app  # assuming this is your FastAPI app

TEST_DB_URL = "sqlite://:memory:"
TEST_MODULES = {"models": ["fast_backend.app.models"]}


@pytest.fixture(scope="session", autouse=True)
async def init_db():
    """
    Create the in-memory test DB once for the whole test session.
    Drop it after all tests are done.
    """
    await Tortoise.init(
        db_url=TEST_DB_URL,
        modules=TEST_MODULES
    )
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


@pytest.fixture
async def db():
    """
    Empty the database between tests to keep them isolated.
    """
    for model in Tortoise.apps["models"].values():
        await model.all().delete()
    yield


@pytest.fixture
async def client():
    """
    HTTP client for endpoint tests (works later when testing FastAPI routes).
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
