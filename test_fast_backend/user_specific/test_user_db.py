# tests/unit/test_user_db.py
import pytest
from uuid import UUID

from fast_backend.app.models.users import User as UserORM
from fast_backend.app.db.users_db import get_user_db
from fast_backend.app.schemas.users import UserCreate, UserRead
from fastapi_users.exceptions import UserNotExists
from fastapi_users_tortoise import TortoiseUserDatabase


@pytest.mark.skip
@pytest.mark.asyncio
@pytest.mark.usefixtures("initialize_database")
class TestUserDatabase:
    """Test suite for user database operations."""

    async def test_get_user_db_returns_tortoise_user_database(
        self, initialize_database
    ):
        """Test that get_user_db returns a TortoiseUserDatabase instance."""
        async for user_db in get_user_db():
            assert isinstance(user_db, TortoiseUserDatabase)

    async def test_initial_database_is_empty(self, initialize_database):
        """Test that the database is empty initially."""
        async for user_db in get_user_db():
            assert await UserORM.all().count() == 0

    async def test_create_user_returns_valid_user(self, initialize_database):
        """Test that creating a user returns a valid user object."""
        async for user_db in get_user_db():
            user_data = {
                "username": "testuser",
                "email": "test@example.com",
                "password": "securepassword",
                "hashed_password": "not none",
            }
            created_user = await user_db.create(user_data)

            assert created_user.id is not None
            assert isinstance(created_user.id, UUID)
            assert isinstance(created_user, UserORM)
            assert created_user.username == "testuser"
            assert created_user.email == "test@example.com"
            assert created_user.hashed_password is not None

    async def test_created_user_has_expected_defaults(self, initialize_database):
        """Test that created users have expected default values."""
        async for user_db in get_user_db():
            # Clear any existing users
            await UserORM.all().delete()

            user_data = {
                "username": "defaultsuser",
                "email": "defaults@example.com",
                "password": "securepassword",
                "hashed_password": "not none",
            }
            created_user = await user_db.create(user_data)

            assert created_user.is_active is True
            # Add other default value checks as needed

    async def test_created_user_is_stored_in_database(self, initialize_database):
        """Test that created users are properly stored in the database."""
        async for user_db in get_user_db():
            # Clear any existing users
            await UserORM.all().delete()

            user_data = {
                "username": "dbuser",
                "email": "db@example.com",
                "password": "securepassword",
                "hashed_password": "not none",
            }
            created_user = await user_db.create(user_data)

            assert await UserORM.all().count() == 1
            user_in_db = await UserORM.get(id=created_user.id)
            assert user_in_db.username == "dbuser"
            assert user_in_db.email == "db@example.com"

    async def test_get_user_by_id(self, initialize_database):
        """Test retrieving a user by ID."""
        async for user_db in get_user_db():
            # Clear any existing users
            await UserORM.all().delete()

            # Create a user directly in the ORM for testing retrieval
            test_user_id = UUID("12345678-1234-5678-1234-567812345678")
            await UserORM.create(
                id=test_user_id,
                username="existinguser",
                email="existing@example.com",
                hashed_password="somehashedpassword",
                is_active=True,
            )

            # Get by ID
            user_by_id = await user_db.get(test_user_id)
            assert user_by_id.username == "existinguser"
            assert isinstance(user_by_id, UserORM)
            assert user_by_id.email == "existing@example.com"

    async def test_get_user_by_email(self, initialize_database):
        """Test retrieving a user by email."""
        async for user_db in get_user_db():
            # Clear any existing users
            await UserORM.all().delete()

            # Create a user directly in the ORM for testing retrieval
            test_user_id = UUID("12345678-1234-5678-1234-567812345678")
            await UserORM.create(
                id=test_user_id,
                username="existinguser",
                email="existing@example.com",
                hashed_password="somehashedpassword",
                is_active=True,
            )

            # Get by email
            user_by_email = await user_db.get_by_email("existing@example.com")
            assert user_by_email.username == "existinguser"
            assert isinstance(user_by_email, UserORM)
            assert user_by_email.id == test_user_id

    async def test_get_nonexistent_user_returns_none(self, initialize_database):
        """Test that getting a non-existent user returns None."""
        async for user_db in get_user_db():
            test_id = UUID("12345678-1234-5678-1234-567812345678")

            non_user = await user_db.get(test_id)
            assert non_user is None

            non_user2 = await user_db.get_by_email("nonexistent@example.com")
            assert non_user2 is None

    async def test_update_user(self, initialize_database):
        """Test updating a user's basic information."""
        async for user_db in get_user_db():
            # Clear any existing users
            await UserORM.all().delete()

            test_user_id = UUID("87654321-4321-8765-4321-876543210000")
            original_user = await UserORM.create(
                id=test_user_id,
                username="updateuser",
                email="update@example.com",
                hashed_password="oldhash",
                is_active=True,
            )

            updated_data = {
                "email": "updated@example.com",
                "username": "updateduser",
                "is_active": True,
                "is_verified": False,
                "is_superuser": False,
            }

            updated_user = await user_db.update(original_user, updated_data)

            assert updated_user.email == "updated@example.com"
            assert updated_user.username == "updateduser"

    async def test_update_user_status(self, initialize_database):
        """Test updating a user's status fields."""
        async for user_db in get_user_db():
            # Clear any existing users
            await UserORM.all().delete()

            test_user_id = UUID("87654321-4321-8765-4321-876543210000")
            original_user = await UserORM.create(
                id=test_user_id,
                username="statususer",
                email="status@example.com",
                hashed_password="oldhash",
                is_active=True,
            )

            updated_data = {
                "email": "status@example.com",
                "username": "statususer",
                "is_active": False,
                "is_verified": True,
                "is_superuser": True,
            }

            updated_user = await user_db.update(original_user, updated_data)

            assert updated_user.is_active is False
            assert updated_user.is_verified is True
            assert updated_user.is_superuser is True

    async def test_update_preserves_password(self, initialize_database):
        """Test that updating a user doesn't change the password hash."""
        async for user_db in get_user_db():
            # Clear any existing users
            await UserORM.all().delete()

            test_user_id = UUID("87654321-4321-8765-4321-876543210000")
            original_user = await UserORM.create(
                id=test_user_id,
                username="pwuser",
                email="pw@example.com",
                hashed_password="oldhash",
                is_active=True,
            )

            updated_data = {
                "email": "updated@example.com",
                "username": "updateduser",
                "is_active": False,
                "is_verified": False,
                "is_superuser": False,
            }

            updated_user = await user_db.update(original_user, updated_data)
            assert updated_user.hashed_password == "oldhash"

    async def test_update_persists_to_database(self, initialize_database):
        """Test that updates are persisted to the database."""
        async for user_db in get_user_db():
            # Clear any existing users
            await UserORM.all().delete()

            test_user_id = UUID("87654321-4321-8765-4321-876543210000")
            original_user = await UserORM.create(
                id=test_user_id,
                username="dbuser",
                email="db@example.com",
                hashed_password="oldhash",
                is_active=True,
            )

            updated_data = {
                "email": "updated@example.com",
                "username": "updateduser",
                "is_active": False,
                "is_verified": False,
                "is_superuser": False,
            }

            await user_db.update(original_user, updated_data)

            # Verify changes in the database
            user_in_db = await UserORM.get(id=test_user_id)
            assert user_in_db.email == "updated@example.com"
            assert user_in_db.is_active is False

    async def test_delete_user(self, initialize_database):
        """Test deleting a user removes them from the database."""
        async for user_db in get_user_db():
            # Clear any existing users
            await UserORM.all().delete()

            test_user_id = UUID("aabbccdd-aabb-ccdd-aabb-ccddaabbccdd")
            await UserORM.create(
                id=test_user_id,
                username="deleteuser",
                email="delete@example.com",
                hashed_password="hash",
                is_active=True,
            )

            assert await UserORM.all().count() == 1

            await user_db.delete(await UserORM.get(id=test_user_id))

            assert await UserORM.all().count() == 0

    async def test_deleted_user_cannot_be_retrieved(self, initialize_database):
        """Test that deleted users cannot be retrieved."""
        async for user_db in get_user_db():
            # Clear any existing users
            await UserORM.all().delete()

            test_user_id = UUID("aabbccdd-aabb-ccdd-aabb-ccddaabbccdd")
            await UserORM.create(
                id=test_user_id,
                username="deleteuser",
                email="delete@example.com",
                hashed_password="hash",
                is_active=True,
            )

            await user_db.delete(await UserORM.get(id=test_user_id))

            deleted_user = await user_db.get(test_user_id)
            assert deleted_user is None
