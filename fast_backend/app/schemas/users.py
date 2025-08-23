# app/schemas/user.py
from typing import Optional
import uuid
from fastapi_users import schemas
from pydantic import Field, BaseModel
from beanie import PydanticObjectId
from fastapi_users import schemas
from datetime import datetime

from .base import SettingsSchema


class UserBase(SettingsSchema):
    username: Optional[str] = None


class UserCreate(UserBase):
    email: str
    password: str
    confirm_password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserUpdate(UserBase):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    


class UserResponse(UserBase, schemas.BaseUser[PydanticObjectId]):
    is_staff: bool = False
    playtesting: list["GameListItem"] = Field(default_factory=list)
    designing: list["GameListItem"] = Field(default_factory=list)
    developing: list["GameListItem"] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class UserListItem(UserBase):
    id: PydanticObjectId
    # there should maybe be two of these, one for staff and one for users


class UserUpdatePermissions(SettingsSchema):
    is_staff: Optional[bool] = None
    is_admin: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_superuser: Optional[bool] = None
    playtesting: Optional[list["GameListItem"]] = None
    designing: Optional[list["GameListItem"]] = None
    developing: Optional[list["GameListItem"]] = None
