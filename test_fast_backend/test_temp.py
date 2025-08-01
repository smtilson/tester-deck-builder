# test_debug_manager.py
import pytest
from unittest.mock import AsyncMock
from fastapi_users import BaseUserManager
from uuid import uuid4

# Import your fixtures and helper functions from their respective locations
from .user_specific.test_user_manager_unit import (
    mock_user_db,
    mock_password_helper,
    unit_user_manager,
)
from .utils.test_helpers import create_mock_user


# Assume a dummy UserManager class to simulate the issue
# If you are NOT overriding create, this is what the AI might have done
# to a different version of your code.
class UserManager(BaseUserManager[object, str]):
    async def create(self, user_create, **kwargs):
        # A bug where 'await' is forgotten
        hashed_password = self.password_helper.hash(
            "some_password"
        )  # <-- Missing await

        # This will fail
        if not isinstance(hashed_password, str):
            raise TypeError(
                f"hashed_password is not a string, but a {type(hashed_password)}"
            )

        return await self.user_db.create({"hashed_password": hashed_password})


# @pytest.mark.skip
@pytest.mark.asyncio
async def test_debug_hash_await(unit_user_manager, mock_password_helper):
    """
    DEBUG TEST: Directly check if the hash call is awaited.
    This test bypasses the UserManager.create method to isolate the `hash` call.
    It should NOT fail if the mocks are set up correctly.
    """

    # Assert that the hash method on the mock is a coroutine
    assert isinstance(mock_password_helper.hash, AsyncMock)

    # Call the mock method and await it
    result = await mock_password_helper.hash("some_password")

    # The result *after* awaiting should be the string
    assert isinstance(result, str)
    assert result == "mock_hashed_password"


# @pytest.mark.skip
@pytest.mark.asyncio
async def test_debug_create_method_logic(unit_user_manager):
    """
    DEBUG TEST: This test will fail if UserManager.create has a bug.
    It simulates a user creation and asserts the type of the hashed password.
    """
    # Create a mock user creation object
    user_create = type(
        "UserCreate",
        (object,),
        {
            "password": "testpassword",
            "email": "test@example.com",
            "username": "testuser",
            "is_active": True,
            "is_verified": False,
        },
    )()

    # This call is where the error is happening
    created_user = await unit_user_manager.create(user_create)

    # This assertion should fail with your current code
    # because created_user.hashed_password is the coroutine object
    # instead of the string result
    assert isinstance(created_user.hashed_password, str)

    # The test should be failing here with an AssertionError
    assert created_user.hashed_password == "mock_hashed_password"
