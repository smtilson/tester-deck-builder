from datetime import datetime
from typing import Optional, Sequence
from beanie import Link, Indexed, PydanticObjectId
from pydantic import Field, BaseModel
from datetime import datetime
from pymongo import IndexModel, ASCENDING

from .base import BaseDocument, BaseLink
from .users import UserLink


class Game(BaseDocument):
    name: str=Indexed(unique=True)
    version: str = "0.0.0"
    description: Optional[str] = None
    designers: Sequence[UserLink] = Field(default_factory=list)
    developers: Sequence[UserLink] = Field(default_factory=list)
    publisher: Optional[str] = None
    release_date: Optional[datetime] = None

    class Settings(BaseDocument.Settings):
        name = "games"
        use_state_management = True  # Enable state management for this model
        is_root = True
        indexes = [
            IndexModel([("name", ASCENDING), ("version", ASCENDING)], unique=True)
        ]

class GameLink(BaseLink):
    link: Link[Game]
