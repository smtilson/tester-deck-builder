import pytest
import uuid
import random
from fastapi_users.exceptions import UserAlreadyExists, UserNotExists
from beanie.odm.fields import PydanticObjectId
from datetime import datetime

from fast_backend.app.crud.users import UserManager
from fast_backend.app.models import User
from fast_backend.app.schemas import UserCreate, UserUpdate, UserResponse


@pytest.mark.skip("standard")
@pytest.mark.usefixtures("init_db")
@pytest.mark.asyncio
class TestUserManagerCreate:
    """Integration tests for UserManager create operations."""

    async def test_create_user_success(self, user_manager, all_test_data):
        """Test successful user creation with valid data."""
        user_data = all_test_data.user
        user_create = UserCreate(**user_data)
        result = await user_manager.create(user_create)

        assert isinstance(result.id, PydanticObjectId)
        assert result.username == user_data["username"]
        assert result.email == user_data["email"]
        assert result.is_staff == False
        assert result.created_at is not None
        assert result.updated_at is None
        assert isinstance(result.playtesting, list)
        assert isinstance(result.designing, list)
        assert isinstance(result.developing, list)
        # Password should not be in response
        assert not hasattr(result, "password")
        assert not hasattr(result, "hashed_password")

        # Check values in database
        db_user = await User.get(result.id)
        assert db_user is not None
        assert db_user.username == user_data["username"]
        assert db_user.email == user_data["email"]
        assert db_user.is_staff == False
        assert db_user.created_at is not None
        assert db_user.updated_at is None
        assert isinstance(db_user.playtesting, list)
        assert isinstance(db_user.designing, list)
        assert isinstance(db_user.developing, list)
        assert db_user.hashed_password is not None

    async def test_create_user_duplicate_username_fails(self, user_manager, all_test_data):
        """Test that creating a user with duplicate username fails."""
        user_data = all_test_data.user
        other_user_data = all_test_data.user
        assert user_data["username"] != other_user_data["username"]
        assert user_data["email"] != other_user_data["email"]
        user_create = UserCreate(**user_data)

        # Create first user
        await user_manager.create(user_create)
        other_user_data["username"] = user_data["username"]
        duplicate_create = UserCreate(**other_user_data)
        with pytest.raises(UserAlreadyExists):
            await user_manager.create(duplicate_create)

    async def test_create_user_duplicate_email_fails(self, user_manager, all_test_data):
        """Test that creating a user with duplicate email fails."""
        user_data = all_test_data.user
        other_user_data = all_test_data.user
        assert user_data["username"] != other_user_data["username"]
        assert user_data["email"] != other_user_data["email"]
        user_create = UserCreate(**user_data)

        # Create first user
        await user_manager.create(user_create)
        other_user_data["email"] = user_data["email"]
        duplicate_create = UserCreate(**other_user_data)
        with pytest.raises(UserAlreadyExists):
            await user_manager.create(duplicate_create)
        
    async def test_create_user_password_is_hashed(self, user_manager, user_test_data):
        """Test that user password is properly hashed during creation."""
        user_data = random.choice(user_test_data)
        original_password = user_data["password"]
        user_create = UserCreate(**user_data)
        result = await user_manager.create(user_create)

        # Verify password was hashed by checking the user in database
        db_user = await User.get(result.id)
        assert db_user is not None
        assert db_user.hashed_password != original_password
        assert db_user.hashed_password.startswith("$")


@pytest.mark.skip("standard")
@pytest.mark.usefixtures("init_db")
@pytest.mark.asyncio
class TestUserManagerRead:
    """Integration tests for UserManager read operations."""

    async def test_get_user_by_id_success(self, user_manager, setup_users):
        """Test successful retrieval of user by ID."""
        created_user = random.choice(setup_users)
        user_id = created_user.id
        result = await user_manager.get(user_id)
        assert result is not None
        assert result.id == user_id
        assert result.username == created_user.username
        assert result.email == created_user.email
        assert result.is_staff == created_user.is_staff
        _ = {"second":0, "microsecond":0}
        assert result.created_at.replace(**_) == created_user.created_at.replace(**_)
        assert result.updated_at == created_user.updated_at
        assert result.playtesting == created_user.playtesting
        assert result.designing == created_user.designing
        assert isinstance(result.developing, list)
        

    async def test_get_user_by_id_not_found(self, user_manager, setup_users):
        non_existent_id = PydanticObjectId()
        with pytest.raises(UserNotExists):
            await user_manager.get(non_existent_id)

    async def test_get_user_by_email_success(self, user_manager, setup_users):
        """Test successful retrieval of user by email."""
        user = random.choice(setup_users)
        result = await user_manager.get_by_email(user.email)
        assert result is not None
        assert result.email == user.email
        assert result.username == user.username
        assert result.id == user.id

    async def test_get_user_by_email_not_found(self, user_manager):
        email = "nonexistent@example.com"
        with pytest.raises(UserNotExists):
            await user_manager.get_by_email(email)

    async def test_get_user_by_username_success(self, user_manager, setup_users):
        """Test successful retrieval of user by username."""
        user_data = random.choice(setup_users)
        result = await user_manager.get_by_username(user_data.username)
        assert result is not None
        assert result.username == user_data.username
        assert result.email == user_data.email
        assert result.id == user_data.id

    async def test_get_user_by_username_not_found(self, user_manager):
        with pytest.raises(UserNotExists):
            await user_manager.get_by_username("nonexistent_user")

    async def test_get_all_users_returns_all(self, user_manager, setup_users):
        """Test that get_all_users returns all created users."""
        result = await user_manager.get_all()
        assert len(result) == len(setup_users)
        assert len(result) > 0
        usernames = [user.username for user in result]
        expected_usernames = [user.username for user in setup_users]
        assert set(usernames) == set(expected_usernames)

    async def test_get_all_users_empty_database(self, user_manager):
        await User.all().delete()
        result = await user_manager.get_all()
        assert result == []


#@pytest.mark.skip("standard")
@pytest.mark.usefixtures("init_db", "single_user")
@pytest.mark.asyncio
class TestUserManagerUpdate:
    """Integration tests for UserManager update operations."""

    async def test_update_user_success(self, user_manager, single_user):
        """Test successful user update."""
        update_data = UserUpdate(
            name=single_user.name + " Updated"
        )
        result = await user_manager.update_user(single_user.id, update_data)
        assert result is not None
        assert result.id == single_user.id
        assert result.name == single_user.name + " Updated"
        # Unchanged fields should remain the same
        assert result.username == single_user.username
        assert result.email == single_user.email

        # Verify update persisted in database
        db_user = await User.get(single_user.id)
        assert db_user is not None
        assert db_user.name == single_user.name + " Updated"
        assert db_user.username == single_user.username
        assert db_user.email == single_user.email

    async def test_update_user_partial_update(self, user_manager, single_user):
        """Test partial user update with only one field."""
        update_data = UserUpdate(name="Only Name Changed")
        result = await user_manager.update_user(single_user.id, update_data)
        assert result is not None
        assert result.name == "Only Name Changed"
        # All other fields should remain unchanged
        assert result.username == single_user.username
        assert result.email == single_user.email
        assert result.is_admin == single_user.is_admin
        assert result.is_staff == single_user.is_staff
        assert result.created_at == single_user.created_at
        assert result.designing == single_user.designing
        assert result.developing == single_user.developing
        assert result.playtesting == single_user.playtesting
        
        db_user = await User.get(single_user.id)
        assert db_user is not None
        assert db_user.name == "Only Name Changed"
        assert db_user.username == single_user.username
        assert db_user.email == single_user.email

    async def test_update_user_empty_update(self, user_manager, single_user):
        """Test update with no fields provided."""
        update_data = UserUpdate()
        result = await user_manager.update_user(single_user.id, update_data)
        assert result is not None
        # All fields should remain unchanged
        assert result.name == single_user.name
        assert result.username == single_user.username
        assert result.email == single_user.email
        assert result.is_admin == single_user.is_admin
        assert result.is_staff == single_user.is_staff
        assert result.created_at == single_user.created_at
        assert result.designing == single_user.designing
        assert result.developing == single_user.developing
        assert result.playtesting == single_user.playtesting
        db_user = await User.get(single_user.id)
        assert db_user is not None
        assert db_user.name == single_user.name
        assert db_user.username == single_user.username
        assert db_user.email == single_user.email

    async def test_update_user_not_found(self, user_manager):
        non_existent_id = PydanticObjectId()
        update_data = UserUpdate(name="New Name")
        result = await user_manager.update_user(non_existent_id, update_data)
        assert result is None


@pytest.mark.skip("standard")
@pytest.mark.usefixtures("init_db", "single_user")
@pytest.mark.asyncio
class TestUserManagerDelete:
    """Integration tests for UserManager delete operations."""

    async def test_delete_user_success(self, user_manager, single_user):
        """Test successful user deletion."""
        result = await user_manager.delete_user(single_user.id)
        assert result is True
        deleted_user = await user_manager.get_user(single_user.id)
        assert deleted_user is None
        db_user = await User.get(single_user.id)
        assert db_user is None

    async def test_delete_user_not_found(self, user_manager):
        non_existent_id = PydanticObjectId()
        result = await user_manager.delete_user(non_existent_id)
        assert result is False
