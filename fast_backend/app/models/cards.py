from datetime import datetime
from typing import Optional

from pydantic import Field
from beanie import Document, Indexed, Link

from .base import BaseDocument
from .games import Game


class Card(BaseDocument):
    name: str = Indexed(str, unique=True)
    game: Optional[Link[Game]] = None
    text: Optional[str] = None
    version: str = "0.0.0"
    # add later
    # card_type: str = Field(default="")
    # traits: list[str] = Field(default_factory=list)
    # image_url: Optional[str] = None

    class Settings(BaseDocument.Settings):
        name = "cards"
        use_state_management = True  # Enable state management for this model
        is_root = True
