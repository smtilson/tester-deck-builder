import pytest
import pytest_asyncio
import uuid
import random
from tortoise.exceptions import IntegrityError

from fast_backend.app.crud.users import UserRepo
from fast_backend.app.models.users import User
from fast_backend.app.schemas.users import UserCreate, UserUpdate


@pytest_asyncio.fixture(scope="function")
async def setup_users(init_db, user_test_data):
    """Create test users for read operations."""
    created_users = []
    for user_data in user_test_data:
        user_create = UserCreate(**user_data)
        created_user = await UserRepo.create_user(user_create)
        created_users.append(created_user)
    return created_users


@pytest_asyncio.fixture(scope="function")
async def setup_single_user(init_db, user_test_data):
    """Create a test user for update operations."""
    user_data = random.choice(user_test_data)
    user_create = UserCreate(**user_data)
    test_user = await UserRepo.create_user(user_create)
    return test_user



@pytest_asyncio.fixture(scope="function")
async def setup_admin(init_db, user_test_data):
    """Create test users with different admin statuses."""
    # Select one admin and one regular user randomly
    user_data = random.choice(user_test_data)
    user_data['is_admin']=True
    admin_user = await UserRepo.create_user(UserCreate(**user_data))
    return admin_user


@pytest.mark.skip("standard")
@pytest.mark.usefixtures("init_db")
@pytest.mark.asyncio
@pytest.mark.asyncio
class TestUserRepoCreate:
    """Integration tests for UserRepo create operations."""

    async def test_create_user_success(self, user_test_data):
        """Test successful user creation with valid data."""
        user_data = random.choice(user_test_data)
        user_create = UserCreate(**user_data)

        result = await UserRepo.create_user(user_create)

        assert result.username == user_data["username"]
        assert result.email == user_data["email"]
        assert result.name == user_data["name"]
        assert result.is_active == user_data["is_active"]
        assert result.is_admin == user_data["is_admin"]
        assert isinstance(result.id, uuid.UUID)
        # Password should not be in response
        assert not hasattr(result, "password")
        assert not hasattr(result, "hashed_password")

        # Verify user exists in database
        db_user = await User.get(id=result.id)
        assert db_user.username == user_data["username"]
        assert db_user.email == user_data["email"]
        assert db_user.is_active == user_data["is_active"]
        assert db_user.hashed_password is not None

    async def test_create_user_duplicate_username_fails(self, user_test_data):
        """Test that creating a user with duplicate username fails."""
        user_data = random.choice(user_test_data)
        user_create = UserCreate(**user_data)

        # Create first user
        await UserRepo.create_user(user_create)

        # Attempt to create second user with same username should fail
        other_users = [user for user in user_test_data if user["username"] != user_data["username"]]
        duplicate_data = random.choice(other_users)
        duplicate_data["username"] = user_data["username"]  # Keep the same username
        duplicate_create = UserCreate(**duplicate_data)

        with pytest.raises(IntegrityError):
            await UserRepo.create_user(duplicate_create)

    async def test_create_user_duplicate_email_fails(self, user_test_data):
        """Test that creating a user with duplicate email fails."""
        user_data = random.choice(user_test_data)
        user_create = UserCreate(**user_data)

        # Create first user
        await UserRepo.create_user(user_create)

        # Attempt to create second user with same email should fail
        other_users = [user for user in user_test_data if user["email"] != user_data["email"]]
        duplicate_data = random.choice(other_users)
        duplicate_data["email"] = user_data["email"]  # Keep the same email
        duplicate_create = UserCreate(**duplicate_data)

        with pytest.raises(IntegrityError):
            await UserRepo.create_user(duplicate_create)

    async def test_create_user_password_is_hashed(self, user_test_data):
        """Test that user password is properly hashed during creation."""
        user_data = random.choice(user_test_data)
        original_password = user_data["password"]
        user_create = UserCreate(**user_data)

        result = await UserRepo.create_user(user_create)

        # Verify password was hashed by checking the user in database
        db_user = await User.get(id=result.id)
        assert db_user.hashed_password != original_password
        assert db_user.hashed_password.startswith("$")  # Hash prefix


# @pytest.mark.skip("standard")
@pytest.mark.usefixtures("init_db")
@pytest.mark.asyncio
@pytest.mark.asyncio
class TestUserRepoRead:
    """Integration tests for UserRepo read operations."""

    async def test_get_user_by_id_success(self, setup_users):
        """Test successful retrieval of user by ID."""
        created_user = random.choice(setup_users)
        user_id = created_user.id

        result = await UserRepo.get_user(user_id)

        assert result is not None
        assert result.id == user_id
        assert result.username == created_user.username
        assert result.email == created_user.email

    async def test_get_user_by_id_not_found(self, setup_users):
        """Test that getting non-existent user returns None."""
        non_existent_id = uuid.uuid4()
        result = await UserRepo.get_user(non_existent_id)
        assert result is None

    async def test_get_user_by_email_success(self, setup_users):
        """Test successful retrieval of user by email."""
        user = random.choice(setup_users)

        result = await UserRepo.get_user_by_email(user.email)

        assert result is not None
        assert result.email == user.email
        assert result.username == user.username
        assert result.id == user.id

    async def test_get_user_by_email_not_found(self):
        """Test that getting user by non-existent email returns None."""
        email = "nonexistent@example.com"
        result = await UserRepo.get_user_by_email(email)

        assert result is None

    async def test_get_user_by_username_success(self, setup_users):
        """Test successful retrieval of user by username."""
        user_data = random.choice(setup_users)

        result = await UserRepo.get_user_by_username(user_data.username)

        assert result is not None
        assert result.username == user_data.username
        assert result.email == user_data.email
        assert result.id == user_data.id

    async def test_get_user_by_username_not_found(self):
        """Test that getting user by non-existent username returns None."""
        result = await UserRepo.get_user_by_username("nonexistent_user")

        assert result is None

    async def test_get_all_users_returns_all(self, user_test_data):
        """Test that get_all_users returns all created users."""
        result = await UserRepo.get_all_users()

        assert len(result) == len(user_test_data)
        usernames = [user.username for user in result]
        expected_usernames = [user["username"] for user in user_test_data]
        assert set(usernames) == set(expected_usernames)

    async def test_get_all_users_empty_database(self):
        """Test get_all_users with empty database."""
        # Clear all users
        from fast_backend.app.models.users import User

        await User.all().delete()

        result = await UserRepo.get_all_users()

        assert result == []


# @pytest.mark.skip("standard")
@pytest.mark.usefixtures("init_db", "setup_user")
@pytest.mark.asyncio
@pytest.mark.asyncio
class TestUserRepoUpdate:
    """Integration tests for UserRepo update operations."""

    async def test_update_user_success(self, setup_user):
        """Test successful user update."""
        update_data = UserUpdate(name="Updated Name", is_admin=True)

        result = await UserRepo.update_user(setup_user.id, update_data)

        assert result is not None
        assert result.id == setup_user.id
        assert result.name == "Updated Name"
        assert result.is_admin is True
        # Unchanged fields should remain the same
        assert result.username == setup_user.username
        assert result.email == setup_user.email

        # Verify update persisted in database
        from fast_backend.app.models.users import User

        db_user = await User.get(id=setup_user.id)
        assert db_user.name == "Updated Name"
        assert db_user.is_admin is True
        assert db_user.username == setup_user.username

    async def test_update_user_partial_update(self, setup_user):
        """Test partial user update with only one field."""
        update_data = UserUpdate(name="Only Name Changed")

        result = await UserRepo.update_user(setup_user.id, update_data)

        assert result is not None
        assert result.name == "Only Name Changed"
        # All other fields should remain unchanged
        assert result.username == setup_user.username
        assert result.email == setup_user.email
        assert result.is_admin == setup_user.is_admin

    async def test_update_user_empty_update(self, setup_user):
        """Test update with no fields provided."""
        update_data = UserUpdate()

        result = await UserRepo.update_user(setup_user.id, update_data)

        assert result is not None
        # All fields should remain unchanged
        assert result.name == setup_user.name
        assert result.username == setup_user.username
        assert result.email == setup_user.email

    async def test_update_user_not_found(self):
        """Test updating non-existent user returns None."""
        non_existent_id = uuid.uuid4()
        update_data = UserUpdate(name="New Name")

        result = await UserRepo.update_user(non_existent_id, update_data)

        assert result is None


# @pytest.mark.skip("standard")
@pytest.mark.usefixtures("init_db", "setup_user")
@pytest.mark.asyncio
@pytest.mark.asyncio
class TestUserRepoDelete:
    """Integration tests for UserRepo delete operations."""

    async def test_delete_user_success(self, setup_user):
        """Test successful user deletion."""
        result = await UserRepo.delete_user(setup_user.id)

        assert result is True

        # Verify user is actually deleted
        deleted_user = await UserRepo.get_user(setup_user.id)
        assert deleted_user is None

        # Verify user no longer exists in database
        from fast_backend.app.models.users import User
        from tortoise.exceptions import DoesNotExist

        with pytest.raises(DoesNotExist):
            await User.get(id=setup_user.id)

    async def test_delete_user_not_found(self):
        """Test deleting non-existent user returns False."""
        non_existent_id = uuid.uuid4()

        result = await UserRepo.delete_user(non_existent_id)

        assert result is False


# blech check these later
@pytest.mark.skip("special")
@pytest.mark.usefixtures("init_db")
@pytest.mark.asyncio
@pytest.mark.asyncio
class TestUserRepoAdminOperations:
    """Integration tests for UserRepo admin-related operations."""

    async def test_is_admin_true_for_admin_user(self, setup_admin):
        """Test is_admin returns True for admin users."""
        result = await UserRepo.is_admin(setup_admin["admin_user"].id)

        assert result is True

    async def test_is_admin_false_for_regular_user(self, setup_admin):
        """Test is_admin returns False for regular users."""
        result = await UserRepo.is_admin(setup_admin["regular_user"].id)

        assert result is False

    async def test_is_admin_false_for_nonexistent_user(self):
        """Test is_admin returns False for non-existent users."""
        non_existent_id = uuid.uuid4()

        result = await UserRepo.is_admin(non_existent_id)

        assert result is False

    async def test_set_admin_status_to_true(self, setup_admin):
        """Test promoting regular user to admin."""
        result = await UserRepo.set_admin_status(setup_admin["regular_user"].id, True)

        assert result is not None
        assert result.is_admin is True

        # Verify in database
        is_admin = await UserRepo.is_admin(setup_admin["regular_user"].id)
        assert is_admin is True

        # Verify directly in database model
        from fast_backend.app.models.users import User

        db_user = await User.get(id=setup_admin["regular_user"].id)
        assert db_user.is_admin is True

    async def test_set_admin_status_to_false(self, setup_admin):
        """Test demoting admin user to regular."""
        result = await UserRepo.set_admin_status(setup_admin["admin_user"].id, False)

        assert result is not None
        assert result.is_admin is False

        # Verify in database
        is_admin = await UserRepo.is_admin(setup_admin["admin_user"].id)
        assert is_admin is False

    async def test_set_admin_status_user_not_found(self):
        """Test setting admin status for non-existent user returns None."""
        non_existent_id = uuid.uuid4()

        result = await UserRepo.set_admin_status(non_existent_id, True)

        assert result is None
