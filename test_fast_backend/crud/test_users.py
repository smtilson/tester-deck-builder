import pytest
import random
from fastapi_users.exceptions import UserAlreadyExists, UserNotExists
from beanie.odm.fields import PydanticObjectId
from datetime import datetime

from fast_backend.app.models import User
from fast_backend.app.schemas import UserCreate, UserUpdate, UserResponse


#@pytest.mark.skip("standard")
@pytest.mark.usefixtures("init_db", "cleanup_db")
@pytest.mark.asyncio
class TestUserManagerCreate:
    """Integration tests for UserManager create operations."""

    async def test_create_user_success(self, managers, data):
        """Test successful user creation with valid data."""
        user_data = data.user
        user_create = UserCreate(**user_data)
        result = await managers.user.create(user_create)

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

    async def test_create_user_duplicate_username_fails(self, managers, data):
        """Test that creating a user with duplicate username fails."""
        user_data_list = list(data.users)
        user_data_1 = user_data_list.pop()
        user_data_2 = user_data_list.pop()
        user_create_1 = UserCreate(**user_data_1)
        user_create_2 = UserCreate(**user_data_2)

        # Create first user
        await managers.user.create(user_create_1)
        user_create_2.username = user_create_1.username
        with pytest.raises(UserAlreadyExists):
            await managers.user.create(user_create_2)

    async def test_create_user_duplicate_email_fails(self, managers, data):
        """Test that creating a user with duplicate email fails."""
        user_data_list = list(data.users)
        user_data_1 = user_data_list.pop()
        user_data_2 = user_data_list.pop()
        user_create_1 = UserCreate(**user_data_1)
        user_create_2 = UserCreate(**user_data_2)

        # Create first user
        await managers.user.create(user_create_1)
        user_create_2.email = user_create_1.email
        with pytest.raises(UserAlreadyExists):
            await managers.user.create(user_create_2)
        
    async def test_create_user_password_is_hashed(self, managers, data):
        """Test that user password is properly hashed during creation."""
        user_data = data.user
        original_password = user_data["password"]
        user_create = UserCreate(**user_data)
        result = await managers.user.create(user_create)

        # Verify password was hashed by checking the user in database
        db_user = await User.get(result.id)
        assert db_user is not None
        assert db_user.hashed_password != original_password
        assert db_user.hashed_password.startswith("$")


#@pytest.mark.skip("standard")
@pytest.mark.usefixtures("init_db", "cleanup_db")
@pytest.mark.asyncio
class TestUserManagerRead:
    """Integration tests for UserManager read operations."""

    async def test_get_user_by_id_success(self, managers, setup):
        """Test successful retrieval of user by ID."""
        user = await setup.user
        user_id = user.id
        result = await managers.user.get(user_id)
        assert result is not None
        assert result.id == user_id
        assert result.username == user.username
        assert result.email == user.email
        assert result.is_staff == user.is_staff
        _ = {"second":0, "microsecond":0}
        assert result.created_at.replace(**_) == user.created_at.replace(**_)
        assert result.updated_at == user.updated_at
        assert result.playtesting == user.playtesting
        assert result.designing == user.designing
        assert isinstance(result.developing, list)
        

    async def test_get_user_by_id_not_found(self, managers, setup):
        non_existent_id = PydanticObjectId()
        with pytest.raises(UserNotExists) as e:
            await managers.user.get(non_existent_id)
        assert str(non_existent_id) in str(e.value)

    async def test_get_user_by_email_success(self, managers, setup):
        """Test successful retrieval of user by email."""
        user = await setup.user
        result = await managers.user.get_by_email(user.email)
        assert result is not None
        assert result.email == user.email
        assert result.username == user.username
        assert result.id == user.id

    async def test_get_user_by_email_not_found(self, managers):
        email = "nonexistent@example.com"
        with pytest.raises(UserNotExists) as e:
            await managers.user.get_by_email(email)
        assert str(email) in str(e.value)

    async def test_get_user_by_username_success(self, managers, setup):
        """Test successful retrieval of user by username."""
        user = await setup.user
        result = await managers.user.get_by_username(user.username)
        assert result is not None
        assert result.username == user.username
        assert result.email == user.email
        assert result.id == user.id

    async def test_get_user_by_username_not_found(self, managers):
        with pytest.raises(UserNotExists) as e:
            await managers.user.get_by_username("nonexistent_user")
        assert str("nonexistent_user") in str(e.value)

    async def test_get_all_users_returns_all(self, managers, setup):
        """Test that get_all_users returns all created users."""
        users = await setup.users()
        result = await managers.user.get_all()
        assert len(result) == len(users)
        assert len(result) > 0
        usernames = [user.username for user in result]
        expected_usernames = [user.username for user in users]
        assert set(usernames) == set(expected_usernames)

    async def test_get_all_users_empty_database(self, managers):
        await managers.user.delete_all()
        result = await managers.user.get_all()
        assert result == []


#@pytest.mark.skip("standard")
@pytest.mark.usefixtures("init_db")
@pytest.mark.asyncio
class TestUserManagerUpdate:
    """Integration tests for UserManager update operations."""

    async def test_update_user_all_fields_success(self, managers, setup):
        """Test successful user update."""
        user = await setup.user
        update_data = UserUpdate(
            id=user.id,
            name=(user.name or '') + " Updated",
            username=(user.username or '') + " Updated",
            email=(user.email or '') + "Updated",
        )
        result = await managers.user.update(update_data)
        assert result is not None
        assert result.id == user.id
        assert result.name == (user.name or '') + " Updated"
        assert result.username == (user.username or '') + " Updated"
        assert result.email == (user.email or '') + "Updated"
        assert result.updated_at is not None
        assert result.is_staff == user.is_staff

        # Verify update persisted in database
        db_user = await User.get(user.id)
        assert db_user is not None
        assert db_user.name == (user.name or '') + " Updated"
        assert db_user.username == (user.username or '') + " Updated"
        assert db_user.email == (user.email or '') + "Updated"

    async def test_update_user_partial_update(self, managers, setup):
        """Test partial user update with only one field."""
        user = await setup.user
        update_data = UserUpdate(id=user.id, name="Only Name Changed")
        result = await managers.user.update(update_data)
        assert result is not None
        assert result.name == "Only Name Changed"
        # All other fields should remain unchanged
        assert result.username == user.username
        assert result.email == user.email
        assert result.is_staff == user.is_staff
        _ = {"second":0,"microsecond":0}
        assert result.created_at.replace(**_) == user.created_at.replace(**_)
        assert result.updated_at is not None
        assert result.designing == user.designing
        assert result.developing == user.developing
        assert result.playtesting == user.playtesting
        
        db_user = await User.get(user.id)
        assert db_user is not None
        assert db_user.name == "Only Name Changed"
        assert db_user.username == user.username
        assert db_user.email == user.email

    async def test_update_user_empty_update(self, managers, setup):
        """Test update with no fields provided."""
        user = await setup.user
        update_data = UserUpdate(id=user.id)
        result = await managers.user.update(update_data)
        assert result is not None
        # All fields should remain unchanged
        assert result.id == user.id
        assert result.name == user.name
        assert result.username == user.username
        assert result.email == user.email
        assert result.is_staff == user.is_staff
        _ = {"second":0,"microsecond":0}
        assert result.created_at.replace(**_) == user.created_at.replace(**_)
        assert result.updated_at is not None

        db_user = await User.get(user.id)
        assert db_user is not None
        assert db_user.name == user.name
        assert db_user.username == user.username
        assert db_user.email == user.email

    async def test_update_user_not_found(self, managers):
        non_existent_id = PydanticObjectId()
        update_data = UserUpdate(name="New Name", id=non_existent_id)
        with pytest.raises(UserNotExists) as e:
            await managers.user.update(update_data)
        assert str(non_existent_id) in str(e.value)


#@pytest.mark.skip("standard")
@pytest.mark.usefixtures("init_db")
@pytest.mark.asyncio
class TestUserManagerDelete:
    """Integration tests for UserManager delete operations."""

    async def test_delete_user_success(self, managers, setup):
        user = await setup.user
        result = await managers.user.delete(user.id)
        assert result is True
        with pytest.raises(UserNotExists) as e:
            await managers.user.get(user.id)
        assert str(user.id) in str(e.value)
        db_user = await User.get(user.id)
        assert db_user is None

    async def test_delete_user_not_found(self, managers):
        non_existent_id = PydanticObjectId()
        with pytest.raises(UserNotExists) as e:
            await managers.user.delete(non_existent_id)
        assert str(non_existent_id) in str(e.value)

# need to add tests that check permission changes work properly.
# also, that is not yet implemented