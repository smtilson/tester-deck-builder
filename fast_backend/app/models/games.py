from datetime import datetime
from typing import Optional
from beanie import Link
from pydantic import Field
from datetime import datetime

from .base import BasicModel


class Game(BasicModel):
    name: str
    description: str
    designers: list[Link["User"]] = Field(default_factory=list)
    publisher: Optional[str] = None
    developers: list[Link["User"]] = Field(default_factory=list)
    release_date: Optional[datetime] = None
    current_version: str = "0.0.0"
    
    class Settings:
        name = "games"