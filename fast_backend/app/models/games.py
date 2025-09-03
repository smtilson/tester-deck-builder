from datetime import datetime
from typing import Optional, Sequence, ClassVar, Type
from beanie import Link, Indexed, PydanticObjectId
from pydantic import Field, BaseModel
from datetime import datetime
from pymongo import IndexModel, ASCENDING

from .base import BaseDocument, LinkHelper
from .links import UserLink, GameLink   


class Game(BaseDocument):
    name: str=Indexed(unique=True)
    version: str = "0.0.0"
    description: Optional[str] = None
    designers: Sequence[UserLink] = Field(default_factory=list)
    developers: Sequence[UserLink] = Field(default_factory=list)
    publisher: Optional[str] = None
    release_date: Optional[datetime] = None

    link_helper: ClassVar[LinkHelper] = LinkHelper(GameLink)

    class Settings(BaseDocument.Settings):
        name = "games"
        use_state_management = True  # Enable state management for this model
        is_root = True
        indexes = [
            IndexModel([("name", ASCENDING), ("version", ASCENDING)], unique=True)
        ]

    
    def to_link(self) -> GameLink:
        return self.link_helper.to_link(self)