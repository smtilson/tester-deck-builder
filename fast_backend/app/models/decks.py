from typing import Annotated, Optional, ClassVar
from beanie import Link, Indexed
from pydantic import Field
from datetime import datetime
from pymongo import IndexModel, ASCENDING
from bson import ObjectId

from .deck_cards import DeckCard
from .links import UserLink, GameLink, DeckLink
from .base import BaseDocument, LinkHelper
from fast_backend.app.schemas import DeckListItem



class Deck(BaseDocument):
    owner: UserLink
    name: str
    game: GameLink
    description: Optional[str] = None
    version: str = "1.0.0"
    is_public: bool = Field(default=False)
    # these should be properties that are computed from the deck_cards
    # is_valid: bool = Field(default=False)
    # in_sync: bool = Field(default=True)
    # similarly version should be a computed field.
    #
    cards: list[DeckCard] = Field(default_factory=list)
    link_helper: ClassVar[LinkHelper] = LinkHelper(DeckLink)
    class Settings(BaseDocument.Settings):
        name = "decks"
        use_state_management = True  # Enable state management for this model
        is_root = True
        indexes = [
            IndexModel([("name", ASCENDING), ("owner", ASCENDING), ("game", ASCENDING), ("version", ASCENDING)], unique=True)
        ]


    def to_link(self):
        return self.link_helper.to_link(self)