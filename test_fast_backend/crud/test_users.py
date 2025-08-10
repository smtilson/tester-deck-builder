import pytest
import uuid
from tortoise.exceptions import IntegrityError

from fast_backend.app.crud.users import UserRepo
from fast_backend.app.schemas.users import UserCreate, UserUpdate
from test_fast_backend.base_class import BaseTestData


class TestUserRepoCreate(BaseTestData):
    """Integration tests for UserRepo create operations."""

    @pytest.mark.asyncio
    async def test_create_user_success(self):
        """Test successful user creation with valid data."""
        user_data = self.get_user_by_username("testuser1")
        user_create = UserCreate(**user_data)
        
        result = await UserRepo.create_user(user_create)
        
        assert result.username == user_data["username"]
        assert result.email == user_data["email"]
        assert result.name == user_data["name"]
        assert result.is_active == user_data["is_active"]
        assert result.is_admin == user_data["is_admin"]
        assert isinstance(result.id, uuid.UUID)
        # Password should not be in response
        assert not hasattr(result, 'password')
        assert not hasattr(result, 'hashed_password')

    @pytest.mark.asyncio
    async def test_create_user_duplicate_username_fails(self):
        """Test that creating a user with duplicate username fails."""
        user_data = self.get_user_by_username("testuser1")
        user_create = UserCreate(**user_data)
        
        # Create first user
        await UserRepo.create_user(user_create)
        
        # Attempt to create second user with same username should fail
        duplicate_data = user_data.copy()
        duplicate_data["email"] = "different@example.com"
        duplicate_create = UserCreate(**duplicate_data)
        
        with pytest.raises(IntegrityError):
            await UserRepo.create_user(duplicate_create)

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email_fails(self):
        """Test that creating a user with duplicate email fails."""
        user_data = self.get_user_by_username("testuser1")
        user_create = UserCreate(**user_data)
        
        # Create first user
        await UserRepo.create_user(user_create)
        
        # Attempt to create second user with same email should fail
        duplicate_data = user_data.copy()
        duplicate_data["username"] = "different_username"
        duplicate_create = UserCreate(**duplicate_data)
        
        with pytest.raises(IntegrityError):
            await UserRepo.create_user(duplicate_create)

    @pytest.mark.asyncio
    async def test_create_user_password_is_hashed(self):
        """Test that user password is properly hashed during creation."""
        user_data = self.get_user_by_username("testuser1")
        original_password = user_data["password"]
        user_create = UserCreate(**user_data)
        
        result = await UserRepo.create_user(user_create)
        
        # Verify password was hashed by checking the user in database
        from fast_backend.app.models.users import User
        db_user = await User.get(id=result.id)
        assert db_user.hashed_password != original_password
        assert db_user.hashed_password.startswith("$")  # Hash prefix


class TestUserRepoRead(BaseTestData):
    """Integration tests for UserRepo read operations."""

    @pytest.fixture(autouse=True)
    async def setup_users(self):
        """Create test users for read operations."""
        for user_data in self.user_data:
            user_create = UserCreate(**user_data)
            await UserRepo.create_user(user_create)

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self):
        """Test successful retrieval of user by ID."""
        user_data = self.get_user_by_username("testuser1")
        user_id = user_data["id"]
        
        result = await UserRepo.get_user(user_id)
        
        assert result is not None
        assert result.id == user_id
        assert result.username == user_data["username"]
        assert result.email == user_data["email"]

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self):
        """Test that getting non-existent user returns None."""
        non_existent_id = uuid.uuid4()
        
        result = await UserRepo.get_user(non_existent_id)
        
        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_by_email_success(self):
        """Test successful retrieval of user by email."""
        user_data = self.get_user_by_username("admin_user")
        
        result = await UserRepo.get_user_by_email(user_data["email"])
        
        assert result is not None
        assert result.email == user_data["email"]
        assert result.username == user_data["username"]

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self):
        """Test that getting user by non-existent email returns None."""
        result = await UserRepo.get_user_by_email("nonexistent@example.com")
        
        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_by_username_success(self):
        """Test successful retrieval of user by username."""
        user_data = self.get_user_by_username("testuser1")
        
        result = await UserRepo.get_user_by_username(user_data["username"])
        
        assert result is not None
        assert result.username == user_data["username"]
        assert result.email == user_data["email"]

    @pytest.mark.asyncio
    async def test_get_user_by_username_not_found(self):
        """Test that getting user by non-existent username returns None."""
        result = await UserRepo.get_user_by_username("nonexistent_user")
        
        assert result is None

    @pytest.mark.asyncio
    async def test_get_all_users_returns_all(self):
        """Test that get_all_users returns all created users."""
        result = await UserRepo.get_all_users()
        
        assert len(result) == len(self.user_data)
        usernames = [user.username for user in result]
        expected_usernames = [user["username"] for user in self.user_data]
        assert set(usernames) == set(expected_usernames)

    @pytest.mark.asyncio
    async def test_get_all_users_empty_database(self):
        """Test get_all_users with empty database."""
        # Clear all users
        from fast_backend.app.models.users import User
        await User.all().delete()
        
        result = await UserRepo.get_all_users()
        
        assert result == []


class TestUserRepoUpdate(BaseTestData):
    """Integration tests for UserRepo update operations."""

    @pytest.fixture(autouse=True)
    async def setup_user(self):
        """Create a test user for update operations."""
        user_data = self.get_user_by_username("testuser1")
        user_create = UserCreate(**user_data)
        self.test_user = await UserRepo.create_user(user_create)

    @pytest.mark.asyncio
    async def test_update_user_success(self):
        """Test successful user update."""
        update_data = UserUpdate(
            name="Updated Name",
            is_admin=True
        )
        
        result = await UserRepo.update_user(self.test_user.id, update_data)
        
        assert result is not None
        assert result.id == self.test_user.id
        assert result.name == "Updated Name"
        assert result.is_admin is True
        # Unchanged fields should remain the same
        assert result.username == self.test_user.username
        assert result.email == self.test_user.email

    @pytest.mark.asyncio
    async def test_update_user_partial_update(self):
        """Test partial user update with only one field."""
        update_data = UserUpdate(name="Only Name Changed")
        
        result = await UserRepo.update_user(self.test_user.id, update_data)
        
        assert result is not None
        assert result.name == "Only Name Changed"
        # All other fields should remain unchanged
        assert result.username == self.test_user.username
        assert result.email == self.test_user.email
        assert result.is_admin == self.test_user.is_admin

    @pytest.mark.asyncio
    async def test_update_user_empty_update(self):
        """Test update with no fields provided."""
        update_data = UserUpdate()
        
        result = await UserRepo.update_user(self.test_user.id, update_data)
        
        assert result is not None
        # All fields should remain unchanged
        assert result.name == self.test_user.name
        assert result.username == self.test_user.username
        assert result.email == self.test_user.email

    @pytest.mark.asyncio
    async def test_update_user_not_found(self):
        """Test updating non-existent user returns None."""
        non_existent_id = uuid.uuid4()
        update_data = UserUpdate(name="New Name")
        
        result = await UserRepo.update_user(non_existent_id, update_data)
        
        assert result is None


class TestUserRepoDelete(BaseTestData):
    """Integration tests for UserRepo delete operations."""

    @pytest.fixture(autouse=True)
    async def setup_user(self):
        """Create a test user for delete operations."""
        user_data = self.get_user_by_username("testuser1")
        user_create = UserCreate(**user_data)
        self.test_user = await UserRepo.create_user(user_create)

    @pytest.mark.asyncio
    async def test_delete_user_success(self):
        """Test successful user deletion."""
        result = await UserRepo.delete_user(self.test_user.id)
        
        assert result is True
        
        # Verify user is actually deleted
        deleted_user = await UserRepo.get_user(self.test_user.id)
        assert deleted_user is None

    @pytest.mark.asyncio
    async def test_delete_user_not_found(self):
        """Test deleting non-existent user returns False."""
        non_existent_id = uuid.uuid4()
        
        result = await UserRepo.delete_user(non_existent_id)
        
        assert result is False


class TestUserRepoAdminOperations(BaseTestData):
    """Integration tests for UserRepo admin-related operations."""

    @pytest.fixture(autouse=True)
    async def setup_users(self):
        """Create test users with different admin statuses."""
        regular_user_data = self.get_user_by_username("testuser1")
        admin_user_data = self.get_user_by_username("admin_user")
        
        self.regular_user = await UserRepo.create_user(UserCreate(**regular_user_data))
        self.admin_user = await UserRepo.create_user(UserCreate(**admin_user_data))

    @pytest.mark.asyncio
    async def test_is_admin_true_for_admin_user(self):
        """Test is_admin returns True for admin users."""
        result = await UserRepo.is_admin(self.admin_user.id)
        
        assert result is True

    @pytest.mark.asyncio
    async def test_is_admin_false_for_regular_user(self):
        """Test is_admin returns False for regular users."""
        result = await UserRepo.is_admin(self.regular_user.id)
        
        assert result is False

    @pytest.mark.asyncio
    async def test_is_admin_false_for_nonexistent_user(self):
        """Test is_admin returns False for non-existent users."""
        non_existent_id = uuid.uuid4()
        
        result = await UserRepo.is_admin(non_existent_id)
        
        assert result is False

    @pytest.mark.asyncio
    async def test_set_admin_status_to_true(self):
        """Test promoting regular user to admin."""
        result = await UserRepo.set_admin_status(self.regular_user.id, True)
        
        assert result is not None
        assert result.is_admin is True
        
        # Verify in database
        is_admin = await UserRepo.is_admin(self.regular_user.id)
        assert is_admin is True

    @pytest.mark.asyncio
    async def test_set_admin_status_to_false(self):
        """Test demoting admin user to regular."""
        result = await UserRepo.set_admin_status(self.admin_user.id, False)
        
        assert result is not None
        assert result.is_admin is False
        
        # Verify in database
        is_admin = await UserRepo.is_admin(self.admin_user.id)
        assert is_admin is False

    @pytest.mark.asyncio
    async def test_set_admin_status_user_not_found(self):
        """Test setting admin status for non-existent user returns None."""
        non_existent_id = uuid.uuid4()
        
        result = await UserRepo.set_admin_status(non_existent_id, True)
        
        assert result is None
