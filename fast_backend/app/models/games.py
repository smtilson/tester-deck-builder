from datetime import datetime
from typing import Optional, Sequence
from beanie import Link, Indexed
from pydantic import Field
from datetime import datetime

from .base import BaseDocument
from .users import User


class Game(BaseDocument):
    name: str=Indexed(unique=True)
    version: str = "0.0.0"
    description: Optional[str] = None
    designers: Sequence[Link[User]] = Field(default_factory=list)
    publisher: Optional[str] = None
    developers: Sequence[Link[User]] = Field(default_factory=list)
    release_date: Optional[datetime] = None

    class Settings(BaseDocument.Settings):
        name = "games"
        use_state_management = True  # Enable state management for this model
        is_root = True
        unique_together = (("name", "version"),)
