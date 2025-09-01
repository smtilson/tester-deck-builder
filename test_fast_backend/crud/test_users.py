import pytest
import random
from fastapi_users.exceptions import UserAlreadyExists, UserNotExists
from beanie.odm.fields import PydanticObjectId
from datetime import datetime
from typing import Optional

from fast_backend.app.models import User
from fast_backend.app.schemas import UserCreate, UserUpdate, UserResponse
from fast_backend.app.exceptions import ValidationError
from fastapi_users.password import PasswordHelper


@pytest.mark.skip("standard")
@pytest.mark.usefixtures("init_db", "cleanup_db")
@pytest.mark.asyncio
class TestUserManagerCreate:
    """Integration tests for UserManager create operations."""

    async def test_create_user_success(self, managers, data) -> None:
        """Test successful user creation with valid data."""
        user_data: dict = data.user
        user_create: UserCreate = UserCreate(**user_data)
        result: Optional[User] = await managers.user.create(user_create)

        assert isinstance(result.id, PydanticObjectId)
        assert result.username == user_data["username"]
        assert result.email == user_data["email"]
        assert result.is_staff == False
        assert result.created_at is not None
        assert result.updated_at is None
        assert isinstance(result.playtesting, list)
        assert isinstance(result.designing, list)
        assert isinstance(result.developing, list)
        # Password should not be in model
        assert not hasattr(result, "password")
        assert hasattr(result, "hashed_password")

        # Check values in database
        db_user: Optional[User] = await User.get(result.id)
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
        assert isinstance(db_user.hashed_password, str)
        assert db_user.hashed_password != data.user["password"]
        assert db_user.hashed_password.startswith("$")  # If using passlib/bcrypt

    async def test_create_user_duplicate_username_fails(self, managers, data) -> None:
        """Test that creating a user with duplicate username fails."""
        user_data_list = list(data.users)
        user_data_1 = user_data_list.pop()
        user_data_2 = user_data_list.pop()
        user_create_1: UserCreate = UserCreate(**user_data_1)
        user_create_2: UserCreate = UserCreate(**user_data_2)

        # Create first user
        await managers.user.create(user_create_1)
        user_create_2.username = user_create_1.username
        with pytest.raises(UserAlreadyExists):
            await managers.user.create(user_create_2)

    async def test_create_user_duplicate_email_fails(self, managers, data) -> None:
        """Test that creating a user with duplicate email fails."""
        user_data_list = list(data.users)
        user_data_1 = user_data_list.pop()
        user_data_2 = user_data_list.pop()
        user_create_1: UserCreate = UserCreate(**user_data_1)
        user_create_2: UserCreate = UserCreate(**user_data_2)

        # Create first user
        await managers.user.create(user_create_1)
        user_create_2.email = user_create_1.email
        with pytest.raises(UserAlreadyExists):
            await managers.user.create(user_create_2)
        
    async def test_create_user_password_is_hashed(self, managers, data) -> None:
        """Test that user password is properly hashed during creation."""
        user_data: dict = data.user
        original_password: str = user_data["password"]
        user_create: UserCreate = UserCreate(**user_data)
        result: Optional[User] = await managers.user.create(user_create)

        # Verify password was hashed by checking the user in database
        db_user: Optional[User] = await User.get(result.id)
        assert db_user is not None
        assert db_user.hashed_password != original_password
        assert db_user.hashed_password.startswith("$")

    async def test_create_user_passwords_do_not_match(self, managers, data) -> None:
        """Test that creating a user with mismatched passwords fails."""
        user_data: dict = data.user.copy()
        user_data["confirm_password"] = "notthesame"
        user_create: UserCreate = UserCreate(**user_data)
        with pytest.raises(ValidationError) as e:
            await managers.user.create(user_create)
        assert "do not match" in str(e.value)
        assert "password" in str(e.value).lower()
        
    async def test_create_user_invalid_email(self, managers, data) -> None:
        """Test that creating a user with invalid email fails."""
        user_data: dict = data.user.copy()
        user_data["email"] = "not-an-email"
        user_create: UserCreate = UserCreate(**user_data)
        with pytest.raises(ValidationError) as e:
            await managers.user.create(user_create)
        assert "A valid email is required" in str(e.value)
        assert "not-an-email" in str(e.value)

    async def test_create_user_empty_fields(self, managers, data) -> None:
        """Test that creating a user with empty fields fails."""
        user_data: dict = data.user.copy()
        for key in user_data.keys():
            empty_data = user_data.copy()
            empty_data[key] = ""
            user_create: UserCreate = UserCreate(**empty_data)
            with pytest.raises(ValidationError) as e:
                await managers.user.create(user_create)
            assert "is required" in str(e.value)
            assert key in str(e.value).lower()

    async def test_create_user_fields_in_response_and_db(self, managers, data) -> None:
        """Test that all expected fields are present in model and DB after creation."""
        user_data: dict = data.user
        user_create: UserCreate = UserCreate(**user_data)
        result: Optional[User] = await managers.user.create(user_create)

        expected_fields = [
            "id", "username", "email", "is_staff", "name",
            "playtesting", "designing", "developing", "created_at", "updated_at"
        ]
        for field in expected_fields:
            assert hasattr(result, field)

        db_user: Optional[User] = await User.get(result.id)
        for field in expected_fields:
            assert hasattr(db_user, field)


@pytest.mark.skip("standard")
@pytest.mark.usefixtures("init_db", "cleanup_db")
@pytest.mark.asyncio
class TestUserManagerRead:
    """Integration tests for UserManager read operations."""

    async def test_get_user_by_id_success(self, managers, setup) -> None:
        """Test successful retrieval of user by ID."""
        user: User = await setup.user
        result: UserResponse = await managers.user.get(user.id)
        assert result is not None
        assert result.id == user.id
        assert result.username == user.username
        assert result.email == user.email
        assert result.is_staff == user.is_staff
        _ = {"second":0, "microsecond":0}
        assert result.created_at.replace(**_) == user.created_at.replace(**_)
        assert result.updated_at == user.updated_at
        assert result.playtesting == user.playtesting
        assert result.designing == user.designing
        assert isinstance(result.developing, list)

    async def test_db_stores_hashed_password(self, managers, setup) -> None:
        user: User = await setup.user
        db_user: Optional[User] = await User.get(user.id)
        assert db_user is not None
        assert db_user.hashed_password is not None
        assert isinstance(db_user.hashed_password, str)
        assert db_user.hashed_password != getattr(user, "password", None)
        

    async def test_get_user_by_id_not_found(self, managers, setup) -> None:
        non_existent_id: PydanticObjectId = PydanticObjectId()
        with pytest.raises(UserNotExists) as e:
            await managers.user.get(non_existent_id)
        assert str(non_existent_id) in str(e.value)

    async def test_get_user_by_email_success(self, managers, setup) -> None:
        """Test successful retrieval of user by email."""
        user: User = await setup.user
        result: UserResponse = await managers.user.get_by_email(user.email)
        assert result is not None
        assert result.email == user.email
        assert result.username == user.username
        assert result.id == user.id

    async def test_get_user_by_email_not_found(self, managers) -> None:
        email: str = "nonexistent@example.com"
        with pytest.raises(UserNotExists) as e:
            await managers.user.get_by_email(email)
        assert str(email) in str(e.value)

    async def test_get_user_by_username_success(self, managers, setup) -> None:
        """Test successful retrieval of user by username."""
        user: User = await setup.user
        result: UserResponse = await managers.user.get_by_username(user.username)
        assert result is not None
        assert result.username == user.username
        assert result.email == user.email
        assert result.id == user.id

    async def test_get_user_by_username_not_found(self, managers) -> None:
        with pytest.raises(UserNotExists) as e:
            await managers.user.get_by_username("nonexistent_user")
        assert str("nonexistent_user") in str(e.value)

    async def test_get_all_users_returns_all(self, managers, setup) -> None:
        """Test that get_all_users returns all created users."""
        users = await setup.users()
        result = await managers.user.get_all()
        assert len(result) == len(users)
        assert len(result) > 0
        usernames = [user.username for user in result]
        expected_usernames = [user.username for user in users]
        assert set(usernames) == set(expected_usernames)

    async def test_get_all_users_empty_database(self, managers) -> None:
        await managers.user.delete_all()
        result = await managers.user.get_all()
        assert result == []


@pytest.mark.skip("standard")
@pytest.mark.usefixtures("init_db")
@pytest.mark.asyncio
class TestUserManagerUpdate:
    """Integration tests for UserManager update operations."""

    async def test_update_user_all_fields_success(self, managers, setup) -> None:
        """Test successful user update."""
        user: User = await setup.user
        update_data: UserUpdate = UserUpdate(
            id=user.id,
            name=(user.name or '') + " Updated",
            username=(user.username or '') + " Updated",
            email=(user.email or '') + "Updated",
        )
        result: UserResponse = await managers.user.update(update_data)
        assert result is not None
        assert result.id == user.id
        assert result.name == (user.name or '') + " Updated"
        assert result.username == (user.username or '') + " Updated"
        assert result.email == (user.email or '') + "Updated"
        assert result.updated_at is not None
        assert result.is_staff == user.is_staff

        # Verify update persisted in database
        db_user: Optional[User] = await User.get(user.id)
        assert db_user is not None
        assert db_user.name == (user.name or '') + " Updated"
        assert db_user.username == (user.username or '') + " Updated"
        assert db_user.email == (user.email or '') + "Updated"

    async def test_update_user_partial_update(self, managers, setup) -> None:
        """Test partial user update with only one field."""
        user: User = await setup.user
        update_data: UserUpdate = UserUpdate(id=user.id, name="Only Name Changed")
        result: UserResponse = await managers.user.update(update_data)
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
        
        db_user: Optional[User] = await User.get(user.id)
        assert db_user is not None
        assert db_user.name == "Only Name Changed"
        assert db_user.username == user.username
        assert db_user.email == user.email

    async def test_update_user_empty_update(self, managers, setup) -> None:
        """Test update with no fields provided."""
        user: User = await setup.user
        update_data: UserUpdate = UserUpdate(id=user.id)
        result: UserResponse = await managers.user.update(update_data)
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

        db_user: Optional[User] = await User.get(user.id)
        assert db_user is not None
        assert db_user.name == user.name
        assert db_user.username == user.username
        assert db_user.email == user.email

    async def test_update_user_not_found(self, managers) -> None:
        non_existent_id: PydanticObjectId = PydanticObjectId()
        update_data: UserUpdate = UserUpdate(name="New Name", id=non_existent_id)
        with pytest.raises(UserNotExists) as e:
            await managers.user.update(update_data)
        assert str(non_existent_id) in str(e.value)


@pytest.mark.skip("standard")
@pytest.mark.usefixtures("init_db")
@pytest.mark.asyncio
class TestUserManagerDelete:
    """Integration tests for UserManager delete operations."""

    async def test_delete_user_success(self, managers, setup) -> None:
        user: User = await setup.user
        result: bool = await managers.user.delete(user.id)
        assert result is True
        with pytest.raises(UserNotExists) as e:
            await managers.user.get(user.id)
        assert str(user.id) in str(e.value)
        db_user: Optional[User] = await User.get(user.id)
        assert db_user is None

    async def test_delete_user_not_found(self, managers) -> None:
        non_existent_id: PydanticObjectId = PydanticObjectId()
        with pytest.raises(UserNotExists) as e:
            await managers.user.delete(non_existent_id)
        assert str(non_existent_id) in str(e.value)


@pytest.mark.skip("standard")
@pytest.mark.usefixtures("init_db", "cleanup_db")
@pytest.mark.asyncio
class TestMisc:
    """Miscellaneous integration tests."""

    async def test_password_helper_instance_on_manager(self, managers, data) -> None:
        """Test that the UserManager has a PasswordHelper instance and it works."""
        user_manager = managers.user
        assert hasattr(user_manager, "password_helper")
        from fastapi_users.password import PasswordHelper
        assert isinstance(user_manager.password_helper, PasswordHelper)

    async def test_password_helper_hash_and_verify(self, managers, data) -> None:
        """Test that PasswordHelper hashes and verifies passwords correctly."""
        password_helper = managers.user.password_helper
        password = "supersecret"
        hashed = password_helper.hash(password)
        assert isinstance(hashed, str)
        assert hashed != password
        verified, _ = password_helper.verify_and_update(password, hashed)
        assert verified is True

    async def test_password_helper_verify_wrong_password(self, managers, data) -> None:
        """Test that PasswordHelper does not verify incorrect passwords."""
        password_helper = managers.user.password_helper
        password = "supersecret"
        wrong_password = "nottherightone"
        hashed = password_helper.hash(password)
        verified, _ = password_helper.verify_and_update(wrong_password, hashed)
        assert verified is False

    async def test_password_hash_matches_helper(self, managers, data) -> None:
        """Test that the stored hashed_password matches the PasswordHelper hash of the original password."""
        user_data: dict = data.user
        original_password: str = user_data["password"]
        user_create: UserCreate = UserCreate(**user_data)
        result: Optional[User] = await managers.user.create(user_create)
        assert result is not None
        db_user: Optional[User] = await User.get(result.id)
        assert db_user is not None

        password_helper = managers.user.password_helper
        verified, _ = password_helper.verify_and_update(original_password, db_user.hashed_password)
        assert verified