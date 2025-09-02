from datetime import datetime
from typing import Annotated, Optional

from pydantic import Field, BaseModel
from beanie import Document, Indexed, Link, PydanticObjectId
from pymongo import IndexModel, ASCENDING

from .base import BaseDocument
from .games import GameLink


class Card(BaseDocument):
    name: str
    game: Optional[GameLink] = None
    text: Optional[str] = None
    version: str = "1.0.0"
    # add later
    # card_type: str = Field(default="")
    # traits: list[str] = Field(default_factory=list)
    # image_url: Optional[str] = None

    def to_link(self) -> "CardLink":
        return CardLink(
            link=Link[Card](self.id, Card),
            id=self.id,
            game=self.game
        )

    class Settings(BaseDocument.Settings):
        name = "cards"
        use_state_management = True  # Enable state management for this model
        is_root = True
        indexes = [
            IndexModel([("name", ASCENDING), ("game", ASCENDING), ("version", ASCENDING)], unique=True)
        ]

class CardLink(BaseLink):
    link: Link[Card]
    game: GameLink
