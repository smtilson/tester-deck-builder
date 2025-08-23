from typing import Optional
from datetime import datetime
from fastapi_users.db import BeanieBaseUser, BeanieUserDatabase
from beanie import Link
from beanie.odm.fields import PydanticObjectId
from pydantic import Field

from .base import BaseDocument


class User(BeanieBaseUser[PydanticObjectId]):
    is_staff: bool = Field(default=False)
    playtesting: list[Link["Game"]] = Field(default_factory=list)  # type: ignore
    designing: list[Link["Game"]] = Field(default_factory=list)  # type: ignore
    developing: list[Link["Game"]] = Field(default_factory=list)  # type: ignore
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    class Settings(BaseDocument.Settings, BeanieBaseUser.Settings):
        name = "users"
        use_state_management = True  # Enable state management for this model
        is_root = True
    

async def get_user_db():
    yield BeanieUserDatabase(User)