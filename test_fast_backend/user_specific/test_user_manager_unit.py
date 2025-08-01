"""Unit tests for UserManager - testing logic with mocked dependencies."""

import pytest
from uuid import UUID
from unittest.mock import AsyncMock, MagicMock, patch

from fast_backend.app.services.user_services.manager import UserManager
from fast_backend.app.schemas.users import UserCreate, UserUpdate
from fast_backend.app.models.users import User
from fastapi_users.exceptions import UserAlreadyExists
from fastapi_users.password import PasswordHelper
from test_fast_backend.utils.test_helpers import create_mock_user
from test_fast_backend.conftest import SAMPLE_USERS


@pytest.fixture
def mock_user_db():
    """Mock user database adapter."""
    mock_db = AsyncMock()
    mock_db._users = {}  # Internal storage for test users

    def get_by_email_side_effect(email: str):
        return mock_db._users.get(email)

    def get_by_id_side_effect(user_id: UUID):
        for user in mock_db._users.values():
            if user.id == user_id:
                return user
        return None

    def create_side_effect(user_data: dict):
        user = create_mock_user(**user_data)
        mock_db._users[user.email] = user
        return user

    mock_db.get_by_email.side_effect = get_by_email_side_effect
    mock_db.get.side_effect = get_by_id_side_effect
    mock_db.create.side_effect = create_side_effect
    mock_db.update.return_value = None
    mock_db.delete.return_value = None

    return mock_db


@pytest.fixture
def mock_password_helper():
    """Mock password helper."""
    mock_helper = MagicMock(spec=PasswordHelper)
    mock_helper.hash = MagicMock(return_value="mock_hashed_password")
    mock_helper.verify_and_update = MagicMock(
        return_value=(True, "mock_hashed_password")
    )
    mock_helper.verify = MagicMock(return_value=True)
    mock_helper.msg = "mock password helper called"
    return mock_helper


@pytest.fixture
def unit_user_manager(mock_user_db, mock_password_helper):
    """UserManager instance with mocked dependencies."""
    manager = UserManager(user_db=mock_user_db, password_helper=mock_password_helper)
    return manager


# # @pytest.mark.skip
@pytest.mark.asyncio
class TestUserManagerUnit:
    """Unit tests for UserManager with mocked dependencies."""

    @patch("fast_backend.app.services.user_services.manager.render_email_template")
    @patch("fast_backend.app.services.worker.queue.enqueue")
    async def test_create_user_success(
        self,
        mock_queue_enqueue,
        mock_render_template,
        unit_user_manager,
        mock_user_db,
        mock_password_helper,
    ):
        """Test successful user creation logic."""
        mock_render_template.return_value = "Mocked Email HTML"
        mock_queue_enqueue.return_value = None

        user_data = SAMPLE_USERS[0]
        user_create = UserCreate(**user_data)

        print(f"\nType of mock_password_helper.hash: {type(mock_password_helper.hash)}")

        created_user = await unit_user_manager.create(user_create)
        print(
            f"Created user's hashed_password: {created_user.hashed_password} (Type: {type(created_user.hashed_password)})"
        )
        # Verify user creation
        assert created_user.email == user_data["email"]
        assert created_user.username == user_data["username"]
        assert created_user.hashed_password == "mock_hashed_password"
        assert created_user.is_active is True
        assert created_user.is_verified is False

        # Verify method calls
        mock_user_db.get_by_email.assert_called_once_with(user_data["email"])
        mock_password_helper.hash.assert_called_once_with(user_data["password"])
        mock_user_db.create.assert_called_once()
        mock_render_template.assert_called_once()
        mock_queue_enqueue.assert_called_once()

    # # @pytest.mark.skip
    async def test_create_user_already_exists(
        self, unit_user_manager, mock_user_db, mock_password_helper
    ):
        """Test UserAlreadyExists exception when user exists."""
        # Add existing user to mock database
        existing_user = create_mock_user(email="existing@example.com")
        mock_user_db._users["existing@example.com"] = existing_user

        user_data = SAMPLE_USERS[0].copy()
        user_data["email"] = "existing@example.com"
        user_create = UserCreate(**user_data)

        with pytest.raises(UserAlreadyExists):
            await unit_user_manager.create(user_create)

        # Verify database create was not called
        mock_user_db.create.assert_not_called()

    # # @pytest.mark.skip
    async def test_authenticate_success(
        self, unit_user_manager, mock_user_db, mock_password_helper
    ):
        """Test successful authentication."""
        # Setup existing user
        user = create_mock_user(
            email="test@example.com", hashed_password="stored_hash", is_active=True
        )
        mock_user_db._users["test@example.com"] = user

        # Mock password verification
        mock_password_helper.verify_and_update.return_value = (True, "stored_hash")
        credentials = MagicMock(username=user.email, password="correct_password")
        authenticated_user = await unit_user_manager.authenticate(credentials)

        assert authenticated_user is user
        mock_user_db.get_by_email.assert_called_once_with("test@example.com")
        mock_password_helper.verify_and_update.assert_called_once_with(
            "correct_password", "stored_hash"
        )

    async def test_authenticate_wrong_password(
        self, unit_user_manager, mock_user_db, mock_password_helper
    ):
        """Test authentication failure with wrong password."""
        user = create_mock_user(
            email="test@example.com", hashed_password="stored_hash", is_active=True
        )
        mock_user_db._users["test@example.com"] = user

        # Mock password verification failure
        mock_password_helper.verify_and_update.return_value = (False, "stored_hash")
        credentials = MagicMock(username=user.email, password="wrong_password")
        authenticated_user = await unit_user_manager.authenticate(credentials)

        assert authenticated_user is None

    # It does not seem like the base class checks for the user to be active or verified.
    # I coould add this by overriding the method, checking those two conditions, adding an early return
    # and then making a call to super.

    async def test_update_user_password(
        self, unit_user_manager, mock_user_db, mock_password_helper
    ):
        """Test updating user password."""
        existing_user = create_mock_user(hashed_password="old_hash")

        # Mock updated user
        updated_user = create_mock_user(hashed_password="new_mock_hash")
        mock_user_db.update.return_value = updated_user
        mock_password_helper.hash.return_value = "new_mock_hash"

        update_data = UserUpdate(password="NewPassword123!")
        result = await unit_user_manager.update(
            user=existing_user, user_update=update_data
        )

        assert result.hashed_password == "new_mock_hash"
        mock_password_helper.hash.assert_called_once_with("NewPassword123!")
        mock_user_db.update.assert_called_once()

    async def test_update_user_other_fields(
        self, unit_user_manager, mock_user_db, mock_password_helper
    ):
        """Test updating non-password fields."""
        existing_user = create_mock_user()

        updated_user = create_mock_user(
            username="updated_username", email="updated@example.com"
        )
        mock_user_db.update.return_value = updated_user

        update_data = UserUpdate(
            username="updated_username", email="updated@example.com"
        )
        result = await unit_user_manager.update(
            user=existing_user, user_update=update_data
        )

        assert result.username == "updated_username"
        assert result.email == "updated@example.com"
        # Password hash should not be called for non-password updates
        mock_password_helper.hash.assert_not_called()
        mock_user_db.update.assert_called_once()
