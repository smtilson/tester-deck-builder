from fastapi_users.db import BeanieBaseUser, BeanieUserDatabase
from beanie import Link
from pydantic import Field

from .base import BaseDocument


class User(BaseDocument, BeanieBaseUser):
    is_staff: bool = Field(default=False)
    playtesting: list[Link["Game"]] = Field(default_factory=list)
    designing: list[Link["Game"]] = Field(default_factory=list)
    developing: list[Link["Game"]] = Field(default_factory=list)

    class Settings:
        name = "users"
