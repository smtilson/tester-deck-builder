# app/schemas/user.py
from typing import Optional
from fastapi_users import schemas
from pydantic import Field, BaseModel
from beanie import PydanticObjectId
from fastapi_users import schemas
from fastapi_users.schemas import CreateUpdateDictModel as CUDM
from datetime import datetime

from .base import SettingsSchema
from .list_items import GameListItem

    
class UserBase(SettingsSchema, CUDM):
    username: str
    email: str


class UserCreate(UserBase):
    password: str
    confirm_password: str

class UserLogin(UserBase):
    username: Optional[str] = None
    email: Optional[str] = None
    password: str


class UserUpdate(UserBase):
    id: PydanticObjectId
    username: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    id: PydanticObjectId
    is_staff: bool = False
    name: Optional[str] = None
    playtesting: list[GameListItem] = Field(default_factory=list)
    designing: list[GameListItem] = Field(default_factory=list)
    developing: list[GameListItem] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class UserUpdatePermissions(SettingsSchema):
    is_staff: Optional[bool] = None
    is_admin: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_superuser: Optional[bool] = None
    playtesting: Optional[list["GameListItem"]] = None
    designing: Optional[list["GameListItem"]] = None
    developing: Optional[list["GameListItem"]] = None
