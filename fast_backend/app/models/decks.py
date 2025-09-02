from typing import Annotated, Optional
from beanie import Link, Indexed
from pydantic import Field
from datetime import datetime
from pymongo import IndexModel, ASCENDING

from .deck_cards import DeckCard
from .users import UserLink
from .base import BaseDocument, BaseLink
from .games import GameLink


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

    def to_link(self) -> "DeckLink":
        return DeckLink(
            link=Link[Deck](self.id, Deck),
            id=self.id,
            name=self.name,
            version=self.version,
            owner=self.owner,
            game=self.game,
            is_public=self.is_public
        )

    class Settings(BaseDocument.Settings):
        name = "decks"
        use_state_management = True  # Enable state management for this model
        is_root = True
        indexes = [
            IndexModel([("name", ASCENDING), ("owner", ASCENDING), ("game", ASCENDING), ("version", ASCENDING)], unique=True)
        ]

class DeckLink(BaseLink):
    link: Link[Deck]
    owner: UserLink
    game: GameLink
    is_public: bool