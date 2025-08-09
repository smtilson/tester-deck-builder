import pytest

from uuid import UUID
from pydantic import ValidationError

from fast_backend.app.crud.users import UserRepo as crud
from fast_backend.app.models.users import User as UserModel
from fast_backend.app.schemas.users import UserCreate, UserRead, UserUpdate

# The conftest.py provides the `initialize_database` fixture which runs automatically
# for each test. We'll also assume it provides a `user_factory` similar to `card_factory`.


@pytest.mark.skip("standard")
@pytest.mark.asyncio
@pytest.mark.usefixtures("initialize_database")
class TestUserCrud:
    """
    Test suite for the User CRUD functions.
    """

    USER_DATA = [
        {
            "username": f"user{i}",
            "email": f"user{i}@example.com",
            "password": f"password{i}",
            # This is here so that some of the tests pass.
            # It is discarded by the creation method of the UserRepo
            "hashed_password": "not none",
            "name": f"User {i}",
        }
        for i in range(1, 4)
    ]

    async def test_create_user(self, initialize_database):
        """Verify that crud.create_user correctly creates a user."""
        # Arrange: Create a Pydantic schema for the new user.
        user_to_create = UserCreate(**self.USER_DATA[0])

        # Act: Call the create_user CRUD function.
        created_user = await crud.create_user(user_to_create)

        # Assert: Check that the returned object is the correct type and has the right data.
        assert isinstance(created_user, UserRead)
        assert isinstance(created_user.id, UUID)
        assert created_user.username == self.USER_DATA[0]["username"]
        assert created_user.email == self.USER_DATA[0]["email"]
        assert created_user.name == self.USER_DATA[0]["name"]
        assert not hasattr(created_user, "password")  # Password should not be returned

        # Assert: Verify it was actually created in the database.
        db_user = await UserModel.get(id=created_user.id)
        assert db_user is not None
        assert db_user.username == self.USER_DATA[0]["username"]
        assert db_user.email == self.USER_DATA[0]["email"]
        assert db_user.name == self.USER_DATA[0]["name"]

    def test_create_user_validation_error(self):
        """Verify that creating a user with invalid data raises a ValidationError."""
        # Arrange: User data missing the required fields.
        invalid_data = {"name": "This user has no username or email"}

        # Act & Assert: Pydantic should raise a validation error on schema creation.
        with pytest.raises(ValidationError):
            UserCreate(**invalid_data)

    async def test_get_user(self, initialize_database, user_factory):
        """Verify that crud.get_user retrieves a user by its ID."""
        # Arrange: Create a user in the DB to retrieve.
        db_user = await user_factory(self.USER_DATA[0])

        # Act: Retrieve the user using the CRUD function.
        retrieved_user = await crud.get_user(db_user.id)

        # Assert: Check that the correct user was returned.
        assert isinstance(retrieved_user, UserRead)
        assert retrieved_user.id == db_user.id
        assert retrieved_user.username == db_user.username
        assert retrieved_user.email == db_user.email
        assert retrieved_user.name == db_user.name

    async def test_get_user_not_found(self, initialize_database):
        """Verify that crud.get_user returns None for a non-existent ID."""
        # Act: Attempt to retrieve a user that doesn't exist.
        non_existent_id = UUID("00000000-0000-0000-0000-000000000000")
        retrieved_user = await crud.get_user(non_existent_id)

        # Assert: The function should return None.
        assert retrieved_user is None

    async def test_get_user_by_email(self, initialize_database, user_factory):
        """Verify that crud.get_user_by_email retrieves a user by its email."""
        # Arrange: Create a user in the DB to retrieve.
        db_user = await user_factory(self.USER_DATA[0])

        # Act: Retrieve the user using the CRUD function.
        retrieved_user = await crud.get_user_by_email(db_user.email)

        # Assert: Check that the correct user was returned.
        assert isinstance(retrieved_user, UserRead)
        assert retrieved_user.id == db_user.id
        assert retrieved_user.username == db_user.username
        assert retrieved_user.email == db_user.email

    async def test_get_user_by_email_not_found(self, initialize_database):
        """Verify that crud.get_user_by_email returns None for a non-existent email."""
        # Act: Attempt to retrieve a user that doesn't exist.
        retrieved_user = await crud.get_user_by_email("nonexistent@example.com")

        # Assert: The function should return None.
        assert retrieved_user is None

    async def test_get_user_by_username(self, initialize_database, user_factory):
        """Verify that crud.get_user_by_username retrieves a user by its username."""
        # Arrange: Create a user in the DB to retrieve.
        db_user = await user_factory(self.USER_DATA[0])

        # Act: Retrieve the user using the CRUD function.
        retrieved_user = await crud.get_user_by_username(db_user.username)

        # Assert: Check that the correct user was returned.
        assert isinstance(retrieved_user, UserRead)
        assert retrieved_user.id == db_user.id
        assert retrieved_user.username == db_user.username
        assert retrieved_user.email == db_user.email

    async def test_get_user_by_username_not_found(self, initialize_database):
        """Verify that crud.get_user_by_username returns None for a non-existent username."""
        # Act: Attempt to retrieve a user that doesn't exist.
        retrieved_user = await crud.get_user_by_username("nonexistent_username")

        # Assert: The function should return None.
        assert retrieved_user is None

    async def test_get_all_users(self, initialize_database, user_factory):
        """Verify that crud.get_all_users retrieves all users."""
        # Arrange: Create multiple users in the DB.
        for user_data in self.USER_DATA:
            await user_factory(user_data)

        # Act: Retrieve all users.
        all_users = await crud.get_all_users()

        # Assert: Check that the list contains the correct number of users.
        assert isinstance(all_users, list)
        assert len(all_users) == len(self.USER_DATA)
        assert all(isinstance(user, UserRead) for user in all_users)

    async def test_update_user(self, initialize_database, user_factory):
        """Verify that crud.update_user correctly updates a user."""
        # Arrange: Create a user to update.
        db_user = await user_factory(self.USER_DATA[0])
        update_data = UserUpdate(
            username="updated_username",
            email="updated@example.com",
            name="Updated Name",
        )

        # Act: Update the user using the CRUD function.
        updated_user = await crud.update_user(db_user.id, update_data)

        # Assert: Check that the returned user has the updated data.
        assert isinstance(updated_user, UserRead)
        assert updated_user.id == db_user.id
        assert updated_user.username == update_data.username
        assert updated_user.email == update_data.email
        assert updated_user.name == update_data.name

        # Assert: Verify the changes were persisted in the database.
        db_user_after_update = await UserModel.get(id=db_user.id)
        assert db_user_after_update.username == update_data.username
        assert db_user_after_update.email == update_data.email
        assert db_user_after_update.name == update_data.name

    async def test_update_user_not_found(self, initialize_database):
        """Verify that crud.update_user returns None for a non-existent ID."""
        # Arrange
        non_existent_id = UUID("00000000-0000-0000-0000-000000000000")
        update_data = UserUpdate(username="this_will_fail")

        # Act
        result = await crud.update_user(non_existent_id, update_data)

        # Assert
        assert result is None

    async def test_delete_user(self, initialize_database, user_factory):
        """Verify that crud.delete_user correctly deletes a user."""
        # Arrange: Create a user to delete.
        db_user = await user_factory(self.USER_DATA[0])
        assert await UserModel.all().count() == 1

        # Act: Delete the user using the CRUD function.
        result = await crud.delete_user(db_user.id)

        # Assert: Check that the function returned True and the user is gone.
        assert result is True
        assert await UserModel.all().count() == 0
        assert await UserModel.get_or_none(id=db_user.id) is None

    async def test_delete_user_not_found(self, initialize_database):
        """Verify that crud.delete_user returns False for a non-existent ID."""
        # Act
        non_existent_id = UUID("00000000-0000-0000-0000-000000000000")
        result = await crud.delete_user(non_existent_id)

        # Assert
        assert result is False

    async def test_is_admin(self, initialize_database, user_factory):
        """Verify that crud.is_admin correctly checks admin status."""
        # Arrange: Create a regular user and an admin user
        user_data = self.USER_DATA[0].copy()
        user_data["is_admin"] = False
        regular_user = await user_factory(user_data)

        admin_data = self.USER_DATA[1].copy()
        admin_data["is_admin"] = True
        admin_user = await user_factory(admin_data)

        # Act & Assert: Check admin status
        assert await crud.is_admin(regular_user.id) is False
        assert await crud.is_admin(admin_user.id) is True

    async def test_is_admin_user_not_found(self, initialize_database):
        """Verify that crud.is_admin returns False for a non-existent ID."""
        # Act
        non_existent_id = UUID("00000000-0000-0000-0000-000000000000")
        result = await crud.is_admin(non_existent_id)

        # Assert
        assert result is False

    async def test_set_admin_status(self, initialize_database, user_factory):
        """Verify that crud.set_admin_status correctly updates admin status."""
        # Arrange: Create a user
        user_data = self.USER_DATA[0].copy()
        user_data["is_admin"] = False
        db_user = await user_factory(user_data)
        assert db_user.is_admin is False

        # Act: Set admin status to True
        updated_user = await crud.set_admin_status(db_user.id, True)

        # Assert: Check that the returned user has updated admin status
        assert isinstance(updated_user, UserRead)
        assert updated_user.is_admin is True

        # Verify the change was persisted in the database
        db_user_after_update = await UserModel.get(id=db_user.id)
        assert db_user_after_update.is_admin is True

        # Act: Set admin status back to False
        updated_user = await crud.set_admin_status(db_user.id, False)

        # Assert: Check that the returned user has updated admin status
        assert updated_user.is_admin is False

        # Verify the change was persisted in the database
        db_user_after_update = await UserModel.get(id=db_user.id)
        assert db_user_after_update.is_admin is False

    async def test_set_admin_status_user_not_found(self, initialize_database):
        """Verify that crud.set_admin_status returns None for a non-existent ID."""
        # Act
        non_existent_id = UUID("00000000-0000-0000-0000-000000000000")
        result = await crud.set_admin_status(non_existent_id, True)

        # Assert
        assert result is None
