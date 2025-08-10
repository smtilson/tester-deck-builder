# app/schemas/user.py
from typing import Optional
import uuid
from fastapi_users import schemas
from pydantic import Field


class UserResponse(schemas.BaseUser[uuid.UUID]):
    """
    Pydantic schema for reading user data (output).
    Inherits from BaseUser and specifies uuid.UUID as the ID type.
    """

    username: str
    email: str
    name: Optional[str] = None
    is_active: bool
    is_superuser: bool
    is_verified: bool
    is_admin: bool  # Is this already included in the base model in the db?
    oauth_accounts: Optional[list] = Field(default_factory=list)


class UserCreate(schemas.BaseUserCreate):
    """
    Pydantic schema for creating a new user (input).
    """

    username: str
    email: str
    password: str
    name: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False
    is_admin: Optional[bool] = (
        False  # Allow setting admin status on creation if desired
    )
    oauth_accounts: Optional[list] = Field(default_factory=list)


class UserUpdate(schemas.BaseUserUpdate):
    """
    Pydantic schema for updating an existing user (input).
    All fields are optional for partial updates.
    """

    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_admin: Optional[bool] = None  # Allow updating admin status
    name: Optional[str] = None
