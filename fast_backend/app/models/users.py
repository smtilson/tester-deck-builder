from typing import Optional
from datetime import datetime
from fastapi_users.db import BeanieBaseUser, BeanieUserDatabase
from beanie import Link, Document
from beanie.odm.fields import PydanticObjectId
from pydantic import Field

from .base import BaseDocument

# Docs say it should be BeanieBaseUser[PydanticObjectId]
# but the documentation on the github repo is different.
class User(BeanieBaseUser, Document):
    username: Optional[str] = None
    email: str
    name: Optional[str] = None
    is_staff: bool = Field(default=False)
    playtesting: list[Link["Game"]] = Field(default_factory=list)  # type: ignore
    designing: list[Link["Game"]] = Field(default_factory=list)  # type: ignore
    developing: list[Link["Game"]] = Field(default_factory=list)  # type: ignore
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    class Settings(BeanieBaseUser.Settings):
        name = "users"
        use_state_management = True  # Enable state management for this model
        is_root = True
    

async def get_user_db():
    yield BeanieUserDatabase(User)  # type: ignore