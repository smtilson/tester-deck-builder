import pytest
import pytest_asyncio
from tortoise.exceptions import DoesNotExist, IntegrityError, ValidationError

from fast_backend.app.models.users import User

# The conftest.py provides the `initialize_database` fixture which runs automatically
# for each test. We'll add a user_factory fixture similar to the card_factory.


@pytest.mark.skip("standard")
@pytest.mark.asyncio
@pytest.mark.usefixtures("initialize_database")
class TestUserModel:
    """
    Test suite for the User model's database operations (CRUD).
    """

    USER_DATA = [
        {
            "email": f"user{i}@example.com",
            "username": f"user{i}",
            "hashed_password": f"hashed_password{i}",
            "name": f"User {i}",
        }
        for i in range(1, 6)
    ]

    @pytest.mark.parametrize("user_data", USER_DATA)
    async def test_create_user(self, user_factory, user_data):
        """Verify that a User can be created in the database."""
        # Arrange: Use the factory to create the user in the database.
        created_user = await user_factory(user_data)

        # Assert: Check that the returned object has the correct data and an ID.
        assert created_user.id is not None
        assert created_user.email == user_data["email"]
        assert created_user.username == user_data["username"]
        assert created_user.name == user_data["name"]
        assert created_user.hashed_password == user_data["hashed_password"]
        assert created_user.is_active is True  # Default value
        assert created_user.is_superuser is False  # Default value
        assert created_user.created_at is not None
        assert created_user.updated_at is not None

        # Assert: Verify it exists in the database by fetching it again.
        db_user = await User.get(id=created_user.id)
        assert db_user is not None

    async def test_email_is_required(self, user_factory):
        """Verify that a User cannot be created without an email."""
        # Arrange: Define user data without the 'email' field.
        user_data = {
            "username": "testuser",
            "hashed_password": "hashedpassword",
            "name": "Test User",
        }

        # Act & Assert: Attempt to create the user and expect a ValidationError.
        with pytest.raises(ValidationError):
            await user_factory(user_data)

    async def test_username_is_required(self, user_factory):
        """Verify that a User cannot be created without a username."""
        # Arrange: Define user data without the 'username' field.
        user_data = {
            "email": "test@example.com",
            "hashed_password": "hashedpassword",
            "name": "Test User",
        }

        # Act & Assert: Attempt to create the user and expect a ValidationError.
        with pytest.raises(ValidationError):
            await user_factory(user_data)

    async def test_hashed_password_is_required(self, user_factory):
        """Verify that a User cannot be created without a hashed_password."""
        # Arrange: Define user data without the 'hashed_password' field.
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "name": "Test User",
        }

        # Act & Assert: Attempt to create the user and expect a ValidationError.
        with pytest.raises(ValidationError):
            await user_factory(user_data)

    async def test_name_is_optional(self, user_factory):
        """Verify that a User can be created without a name."""
        # Arrange: Define user data without the 'name' field.
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "hashed_password": "hashedpassword",
        }

        # Act: Create the user using the factory.
        created_user = await user_factory(user_data)

        # Assert: Check that the user was created successfully.
        assert created_user.id is not None
        assert created_user.email == user_data["email"]
        assert created_user.username == user_data["username"]
        assert created_user.name is None

    @pytest.mark.parametrize("user_data", USER_DATA)
    async def test_read_user(self, user_factory, user_data):
        """Verify that a User can be read from the database."""
        # Arrange: Create a user to be read.
        created_user = await user_factory(user_data)

        # Act: Fetch the user by its ID.
        read_user = await User.get(id=created_user.id)

        # Assert: Check that the fetched data is correct.
        assert read_user.id == created_user.id
        assert read_user.email == user_data["email"]
        assert read_user.username == user_data["username"]
        assert read_user.name == user_data["name"]

    @pytest.mark.parametrize("user_data", USER_DATA)
    async def test_update_user(self, user_factory, user_data):
        """Verify that a User's attributes can be updated."""
        # Arrange: Create a user.
        user = await user_factory(user_data)
        original_updated_at = user.updated_at

        # Act: Update its name and save it.
        new_name = f"{user_data['name']} Updated"
        user.name = new_name
        await user.save()

        # Assert: Fetch the user again and check if the update was persisted.
        updated_user = await User.get(id=user.id)
        assert updated_user.name == new_name
        # Verify the updated_at timestamp has changed.
        assert updated_user.updated_at > original_updated_at

    @pytest.mark.parametrize("user_data", USER_DATA)
    async def test_delete_user(self, user_factory, user_data):
        """Verify that a User can be deleted from the database."""
        # Arrange: Create a user to be deleted.
        user_to_delete = await user_factory(user_data)
        user_id = user_to_delete.id

        # Confirm it's in the database before deletion.
        assert await User.all().count() == 1

        # Act: Delete the user.
        await user_to_delete.delete()

        # Assert: Confirm it's no longer in the database.
        assert await User.all().count() == 0
        with pytest.raises(DoesNotExist):
            await User.get(id=user_id)

    async def test_uniqu_e_email_constraint(self, user_factory):
        """Verify that a User cannot be created with a duplicate email."""
        # Arrange: Create a user with a specific email.
        user_data = {
            "email": "unique@example.com",
            "username": "uniqueuser",
            "hashed_password": "hashedpassword",
            "name": "Unique User",
        }
        await user_factory(user_data)

        # Act & Assert: Attempt to create another user with the same email.
        duplicate_data = {
            "email": "unique@example.com",  # Same email
            "username": "differentuser",
            "hashed_password": "differentpassword",
            "name": "Different User",
        }
        with pytest.raises(IntegrityError):
            await user_factory(duplicate_data)

    async def test_unique_username_constraint(self, user_factory):
        """Verify that a User cannot be created with a duplicate username."""
        # Arrange: Create a user with a specific username.
        user_data = {
            "email": "user1@example.com",
            "username": "sameusername",
            "hashed_password": "hashedpassword",
            "name": "First User",
        }
        await user_factory(user_data)

        # Act & Assert: Attempt to create another user with the same username.
        duplicate_data = {
            "email": "user2@example.com",
            "username": "sameusername",  # Same username
            "hashed_password": "differentpassword",
            "name": "Second User",
        }
        with pytest.raises(IntegrityError):
            await user_factory(duplicate_data)

    async def test_str_representation(self, user_factory):
        """Verify the string representation of the User model."""
        # Test with username
        user_data = {
            "email": "str_test@example.com",
            "username": "strtest",
            "hashed_password": "hashedpassword",
            "name": "String Test",
        }
        user = await user_factory(user_data)
        assert str(user) == "strtest"
