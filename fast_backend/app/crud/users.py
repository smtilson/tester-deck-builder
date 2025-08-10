from typing import Optional
import uuid
from fastapi_users.password import PasswordHelper
from passlib.context import CryptContext


from fast_backend.app.models.users import User as UserModel
from fast_backend.app.schemas.users import UserCreate, UserUpdate, UserResponse


class UserRepo:
    context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")
    password_helper = PasswordHelper(context)

    @staticmethod
    async def create_user(user_data: UserCreate) -> UserResponse:
        """
        Create a user with a hashed password.

        Args:
            user_data: The user data from the request

        Returns:
            The created user as a Pydantic schema instance.
        """

        # Create a dict with all user data except password
        user_dict = user_data.model_dump(exclude={"password"})

        # Hash the password and add it to the dict
        user_dict["hashed_password"] = UserRepo.password_helper.hash(user_data.password)

        # Create the user with the hashed password
        user_obj = await UserModel.create(**user_dict)
        return UserResponse.model_validate(user_obj)

    @staticmethod
    async def get_user(user_id: uuid.UUID) -> Optional[UserResponse]:
        """
        Get a user by their ID.

        Args:
            user_id: The uuid.UUID of the user to retrieve

        Returns:
            The user as a Pydantic schema, or None if it doesn't exist.
        """
        user_obj = await UserModel.get_or_none(id=user_id)
        if user_obj:
            return UserResponse.model_validate(user_obj)
        return None

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[UserResponse]:
        """
        Get a user by their email.

        Args:
            email: The email of the user to retrieve

        Returns:
            The user as a Pydantic schema, or None if it doesn't exist.
        """
        user_obj = await UserModel.get_or_none(email=email)
        if user_obj:
            return UserResponse.model_validate(user_obj)
        return None

    @staticmethod
    async def get_user_by_username(username: str) -> Optional[UserResponse]:
        """
        Get a user by their username.

        Args:
            username: The username of the user to retrieve

        Returns:
            The user as a Pydantic schema, or None if it doesn't exist.
        """
        user_obj = await UserModel.get_or_none(username=username)
        if user_obj:
            return UserResponse.model_validate(user_obj)
        return None

    @staticmethod
    async def get_all_users() -> list[UserResponse]:
        """
        Get all users.

        Returns:
            A list of all users as Pydantic schema instances.
        """
        user_objs = await UserModel.all()
        return [UserResponse.model_validate(user) for user in user_objs]

    @staticmethod
    async def update_user(
        user_id: uuid.UUID, user_data: UserUpdate
    ) -> Optional[UserResponse]:
        """
        Update a user.

        Args:
            user_id: The uuid.UUID of the user to update
            user_data: The updated user data from the request

        Returns:
            The updated user as a Pydantic schema, or None if the user doesn't exist.
        """
        user_obj = await UserModel.get_or_none(id=user_id)
        if user_obj:
            # Use model_dump(exclude_unset=True) to only get provided fields
            update_data = user_data.model_dump(exclude_unset=True)
            if update_data:  # Only update if there is data
                await user_obj.update_from_dict(update_data).save()
            return UserResponse.model_validate(user_obj)
        return None

    @staticmethod
    async def delete_user(user_id: uuid.UUID) -> bool:
        """
        Delete a user.

        Args:
            user_id: The uuid.UUID of the user to delete

        Returns:
            True if the user was deleted, False if it doesn't exist
        """
        user_obj = await UserModel.get_or_none(id=user_id)
        if user_obj:
            await user_obj.delete()
            return True
        return False

    @staticmethod
    async def is_admin(user_id: uuid.UUID) -> bool:
        """
        Check if a user is an admin.

        Args:
            user_id: The uuid.UUID of the user to check

        Returns:
            True if the user is an admin, False otherwise
        """
        user_obj = await UserModel.get_or_none(id=user_id)
        if user_obj:
            return user_obj.is_admin
        return False

    @staticmethod
    async def set_admin_status(
        user_id: uuid.UUID, is_admin: bool
    ) -> Optional[UserResponse]:
        """
        Set a user's admin status.

        Args:
            user_id: The uuid.UUID of the user to update
            is_admin: The new admin status

        Returns:
            The updated user as a Pydantic schema, or None if the user doesn't exist.
        """
        user_obj = await UserModel.get_or_none(id=user_id)
        if user_obj:
            user_obj.is_admin = is_admin
            await user_obj.save()
            return UserResponse.model_validate(user_obj)
        return None
