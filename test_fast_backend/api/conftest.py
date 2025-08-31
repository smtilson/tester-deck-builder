import pytest
import pytest_asyncio
from httpx import AsyncClient
from fastapi import FastAPI
from fast_backend.app.api.endpoints.auth import auth_router

@pytest_asyncio.fixture(scope="function")
def event_loop():
    """Create an event loop for async tests."""
    import asyncio
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="function")
async def test_app(init_db) -> FastAPI:
    """Create a FastAPI app instance with the auth router for testing."""
    app = FastAPI()
    app.include_router(auth_router)
    # Optionally, do any DB setup here
    return app

@pytest_asyncio.fixture(scope="function")
async def client(test_app: FastAPI) -> AsyncClient:
    """Create an AsyncClient for making requests to the test app."""
    async with AsyncClient(app=test_app, base_url="http://test") as ac:
        yield ac

# You can add more fixtures here for test users, tokens, etc.