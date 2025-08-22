from typing import Optional
from beanie import Link
from pydantic import Field
from datetime import datetime

from .deck_cards import DeckCard
from .old_users import User
from .base import BasicModel

class Deck(BasicModel):
    owner: Link[User]
    name: str
    game: str
    description: Optional[str] = None
    is_public: bool = Field(default=False)
    is_valid: bool = Field(default=False)
    # this should be a property that is computed from the deck_cards
    # in_sync: bool = Field(default=True)   
    # similarly version should be a computed field. 
    cards: list[DeckCard] = Field(default_factory=list)
    
    class Settings:
        name="decks"