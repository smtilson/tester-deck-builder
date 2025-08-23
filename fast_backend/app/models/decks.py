from typing import Optional
from beanie import Link
from pydantic import Field
from datetime import datetime

from .deck_cards import DeckCard
from .users import User
from .base import BaseDocument
from .games import Game


class Deck(BaseDocument):
    owner: Link[User]
    name: str
    game: Link[Game]
    description: Optional[str] = None
    is_public: bool = Field(default=False)
    # these should be properties that are computed from the deck_cards
    # is_valid: bool = Field(default=False)
    # in_sync: bool = Field(default=True)
    # similarly version should be a computed field.
    cards: list[DeckCard] = Field(default_factory=list)

    class Settings(BaseDocument.Settings):
        name = "decks"
        use_state_management = True  # Enable state management for this model
        is_root = True
