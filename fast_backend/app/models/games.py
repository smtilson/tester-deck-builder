from datetime import datetime
from typing import Optional
from beanie import Link
from pydantic import Field
from datetime import datetime

from .base import BaseDocument


class Game(BaseDocument):
    name: str
    version: str = "0.0.0"
    description: Optional[str] = None
    designers: list[Link["User"]] = Field(default_factory=list)
    publisher: Optional[str] = None
    developers: list[Link["User"]] = Field(default_factory=list)
    release_date: Optional[datetime] = None

    class Settings:
        name = "games"
