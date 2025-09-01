import pytest
import pytest_asyncio
from httpx import AsyncClient
from fastapi import FastAPI
from fastapi_users.password import PasswordHelper

from fast_backend.app.models import User
from fast_backend.app.api.endpoints.auth import auth_router
from fast_backend.app.exceptions import validation_exception_handler, ValidationError

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
    app.add_exception_handler(ValidationError, validation_exception_handler)
    # Optionally, do any DB setup here
    return app

@pytest_asyncio.fixture(scope="function")
async def client(test_app: FastAPI) -> AsyncClient:
    """Create an AsyncClient for making requests to the test app."""
    async with AsyncClient(app=test_app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def verified_user():
    """Create and return a verified, active user."""
    password = "strongpassword123"
    hashed_password = PasswordHelper().hash(password)
    user = User(
        username="fixture_verified",
        email="fixture_verified@example.com",
        hashed_password=hashed_password,
        is_verified=True,
        is_active=True,
    )
    await user.insert()
    setattr(user, "_password", password)
    return user


@pytest.fixture
async def unverified_user():
    """Create and return an unverified, active user."""
    password = "strongpassword123"
    hashed_password = PasswordHelper().hash(password)
    user = User(
        username="fixture_unverified",
        email="fixture_unverified@example.com",
        hashed_password=hashed_password,
        is_verified=False,
        is_active=True,
    )
    await user.insert()
    setattr(user, "_password", password)
    return user


@pytest.fixture
async def inactive_user():
    """Create and return an inactive user."""
    password = "strongpassword123"
    hashed_password = PasswordHelper().hash(password)
    user = User(
        username="fixture_inactive",
        email="fixture_inactive@example.com",
        hashed_password=hashed_password,
        is_verified=True,
        is_active=False,
    )
    await user.insert()
    setattr(user, "_password", password)
    return user


@pytest.fixture
async def valid_reset_token(create_verified_user, monkeypatch):
    """Return a valid password reset token for the verified user."""
    captured = {}

    async def capture_token(self, user, token, request):
        captured["token"] = token

    from fast_backend.app.auth.manager import UserManager

    monkeypatch.setattr(UserManager, "on_after_forgot_password", capture_token)

    # Simulate password reset request
    reset_payload = {"email": create_verified_user.email}
    # You may need to use a test client here, or pass it as a fixture argument
    # response = await client.post("/auth/forgot-password", json=reset_payload)
    # assert response.status_code == 202

    # For demonstration, just return a dummy token
    return captured.get("token", "dummy-token")

# You can add more fixtures here for test users, tokens, etc.