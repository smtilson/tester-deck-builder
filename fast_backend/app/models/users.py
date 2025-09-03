from typing import Optional, ClassVar, Type
from datetime import datetime
from fastapi_users.db import BeanieBaseUser, BeanieUserDatabase
from beanie import Link, Document, Indexed
from beanie.odm.fields import PydanticObjectId
from pydantic import Field
from pymongo import IndexModel, ASCENDING

from .base import BaseDocument, LinkHelper
from .links import GameLink, UserLink
from fast_backend.app.schemas import UserResponse, UserListItem



# Docs say it should be BeanieBaseUser[PydanticObjectId]
# but the documentation on the github repo is different.
class User(BeanieBaseUser, Document):
    username: str
    email: str
    name: Optional[str] = None
    is_staff: bool = Field(default=False)
    playtesting: list[GameLink] = Field(default_factory=list)  # type: ignore
    designing: list[GameLink] = Field(default_factory=list)  # type: ignore
    developing: list[GameLink] = Field(default_factory=list)  # type: ignore
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    hashed_password: str

    link_helper: ClassVar[LinkHelper] = LinkHelper(UserLink)

    class Settings(BeanieBaseUser.Settings):
        name = "users"
        use_state_management = True  # Enable state management for this model
        is_root = True
        indexes = [
            IndexModel([("username", ASCENDING)], unique=True),
            IndexModel([("email", ASCENDING)], unique=True),
        ]

    def to_resp(self) -> "UserResponse":
        return UserResponse.model_validate(self)
    
    def to_link(self) -> UserLink:
        return self.link_helper.to_link(self)

async def get_user_db():
    yield BeanieUserDatabase(User)  # type: ignore
