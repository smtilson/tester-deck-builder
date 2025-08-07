"""Integration tests for UserManager - testing with real database."""

import pytest
from uuid import UUID
from unittest.mock import patch, MagicMock, AsyncMock

from fast_backend.app.models.users import User as UserORM
from fast_backend.app.schemas.users import UserCreate, UserUpdate
from fast_backend.app.core.config import Environment, settings
from fastapi_users.exceptions import (
    UserAlreadyExists,
    InvalidPasswordException,
    UserNotExists,
)
from test_fast_backend.conftest import SAMPLE_USERS


@pytest.fixture
def mock_token_generator():
    """
    Creates a mock token generator to replace the real one.
    This prevents the UserManager from trying to connect to a real cache.
    """
    # Create the mock object
    mock_generator = MagicMock()

    # Configure its expected method returns
    mock_generator.generate.return_value = "mock_token"
    mock_generator.verify.return_value = "mock_user_id"
    mock_generator.create.return_value = "mock_token_payload"

    return mock_generator


@pytest.mark.skip
@pytest.mark.asyncio
@pytest.mark.usefixtures("initialize_database")
class TestUserManagerIntegration:
    """Integration tests for UserManager with real database interactions."""

    async def test_create_user_success(
        self,
        initialize_database,
        # mock_queue_enqueue, mock_render_template,
        mock_on_after_register_spy,
        user_manager,
    ):
        """Test successful user creation with email and queue callbacks."""
        # mock_render_template.return_value = "Welcome email HTML"
        # mock_queue_enqueue.return_value = None
        print("test started")
        user_data = SAMPLE_USERS[0]
        user_create = UserCreate(**user_data)
        print("creating user")
        created_user = await user_manager.create(user_create)
        print("user created")
        print("asserting facts")
        # Verify user creation
        assert created_user.id is not None
        assert isinstance(created_user.id, UUID)
        assert created_user.username == user_data["username"]
        assert created_user.email == user_data["email"]
        assert created_user.name == user_data["name"]
        assert created_user.hashed_password is not None
        assert created_user.is_active is True
        assert created_user.is_superuser is False
        assert created_user.is_verified is False
        print("done asserting things about created_user, checing passwordd")
        # Verify password was hashed correctly
        password_valid, _ = user_manager.password_helper.verify_and_update(
            user_data["password"], created_user.hashed_password
        )
        assert password_valid is True
        print("done checking password")
        print("checking db for user")
        # Verify database persistence
        user_in_db = await UserORM.get(id=created_user.id)
        assert user_in_db.email == user_data["email"]
        assert user_in_db.username == user_data["username"]
        print("checking method calls")
        # Verify callbacks were called
        mock_on_after_register_spy.called_once()
        mock_on_after_register_spy.render_email_template.assert_called_once()
        mock_on_after_register_spy.queue_enqueue.enqueue.assert_called_once()

    async def test_create_user_duplicate_email(self, initialize_database, user_manager):
        """Test that creating a user with existing email raises UserAlreadyExists."""
        user_data = SAMPLE_USERS[0]
        user_create = UserCreate(**user_data)

        # Create first user
        await user_manager.create(user_create)

        # Try to create second user with same email
        duplicate_data = SAMPLE_USERS[1].copy()
        duplicate_data["email"] = user_data["email"]  # Same email
        duplicate_create = UserCreate(**duplicate_data)

        with pytest.raises(UserAlreadyExists):
            await user_manager.create(duplicate_create)

    async def test_create_user_duplicate_username(
        self, initialize_database, user_manager
    ):
        """Test that creating a user with existing username raises UserAlreadyExists."""
        user_data = SAMPLE_USERS[0]
        user_create = UserCreate(**user_data)

        # Create first user
        await user_manager.create(user_create)

        # Try to create second user with same username
        duplicate_data = SAMPLE_USERS[1].copy()
        duplicate_data["username"] = user_data["username"]  # Same username
        duplicate_create = UserCreate(**duplicate_data)

        with pytest.raises(UserAlreadyExists):
            await user_manager.create(duplicate_create)

    async def test_authenticate_success(self, initialize_database, user_manager):
        """Test successful authentication with correct credentials."""
        user_data = SAMPLE_USERS[0]
        user_create = UserCreate(**user_data)
        created_user = await user_manager.create(user_create)

        credentials = MagicMock(
            username=user_data["email"], password=user_data["password"]
        )
        authenticated_user = await user_manager.authenticate(credentials)

        assert authenticated_user is not None
        assert authenticated_user.email == created_user.email
        assert authenticated_user.id == created_user.id

    async def test_authenticate_wrong_password(self, initialize_database, user_manager):
        """Test authentication failure with incorrect password."""
        user_data = SAMPLE_USERS[0]
        user_create = UserCreate(**user_data)
        await user_manager.create(user_create)
        credentials = MagicMock(username=user_data["email"], password="Wrong password")
        authenticated_user = await user_manager.authenticate(credentials)

        assert authenticated_user is None

    async def test_validate_password_dev_environment(
        self, initialize_database, user_manager
    ):
        """Test password validation in development environment."""
        user = UserORM(email="test@example.com", username="test", hashed_password="abc")
        password = "ValidPassword123!"

        # Should not raise exception in dev environment
        await user_manager.validate_password(password, user)

    async def test_validate_password_prod_environment(
        self, initialize_database, user_manager
    ):
        """Test password validation in production environment."""
        user = UserORM(email="test@example.com", username="test", hashed_password="abc")

        with patch.object(settings, "ENVIRONMENT", Environment.prod):
            # Test too short password
            with pytest.raises(InvalidPasswordException, match="at least 8 characters"):
                await user_manager.validate_password("short", user)

            # Test password containing email
            with pytest.raises(InvalidPasswordException, match="not contain e-mail"):
                await user_manager.validate_password("test@example.com123", user)

            # Test only alphabetic password
            with pytest.raises(
                InvalidPasswordException,
                match="at least one number or special characters",
            ):
                await user_manager.validate_password("OnlyLetters", user)

            # Test only numeric password
            with pytest.raises(
                InvalidPasswordException, match="not contain only numeric values"
            ):
                await user_manager.validate_password("123456789", user)

    async def test_update_user_password(self, initialize_database, user_manager):
        """Test updating a user's password."""
        user_data = SAMPLE_USERS[0]
        user_create = UserCreate(**user_data)
        created_user = await user_manager.create(user_create)
        old_password_hash = created_user.hashed_password

        update_data = UserUpdate(password="NewPassword456!")
        updated_user = await user_manager.update(
            user=created_user, user_update=update_data
        )

        # Verify password was changed
        assert updated_user.hashed_password != old_password_hash

        # Verify old password no longer works
        credentials = MagicMock(
            username=user_data["email"], password=user_data["password"]
        )

        assert await user_manager.authenticate(credentials) is None

        # Verify new password works
        new_credentials = MagicMock(
            username=user_data["email"], password="NewPassword456!"
        )
        assert await user_manager.authenticate(new_credentials) is not None

    async def test_update_user_fields(self, initialize_database, user_manager):
        """Test updating non-password user fields."""
        user_data = SAMPLE_USERS[0]
        user_create = UserCreate(**user_data)
        created_user = await user_manager.create(user_create)

        update_data = UserUpdate(
            username="updated_username",
            email="updated@example.com",
            name="Updated Name",
            is_active=False,
        )
        updated_user = await user_manager.update(
            user=created_user, user_update=update_data
        )

        # Verify updates
        assert updated_user.username == "updated_username"
        assert updated_user.email == "updated@example.com"
        assert updated_user.name == "Updated Name"
        assert updated_user.is_active is False
        assert updated_user.hashed_password == created_user.hashed_password  # Unchanged

        # Verify in database
        user_in_db = await UserORM.get(id=created_user.id)
        assert user_in_db.username == "updated_username"
        assert user_in_db.email == "updated@example.com"

    async def test_delete_user(self, initialize_database, user_manager):
        """Test deleting a user."""
        user_data = SAMPLE_USERS[0]
        user_create = UserCreate(**user_data)
        created_user = await user_manager.create(user_create)

        # Verify user exists
        assert await UserORM.all().count() == 1

        await user_manager.delete(created_user)

        # Verify user is deleted
        assert await UserORM.all().count() == 0
        with pytest.raises(UserNotExists):
            await user_manager.get(created_user.id)
