"""
Database models using Beanie ODM.
"""

from .users import User, get_user_db
from .cards import Card
from .decks import Deck
from .deck_cards import DeckCard
from .games import Game
from .links import CardLink, DeckLink, GameLink, UserLink, MinLink, BaseLink
from .base import BaseDocument, LinkHelper

__all__ = [
    "User",
    "Card",
    "Deck",
    "DeckCard",
    "Game",
    "BaseDocument",
    "get_user_db",
    "UserLink",
    "CardLink",
    "DeckLink",
    "GameLink",
    "BaseLink",
    "MinLink",
    "LinkHelper"
]

User.model_rebuild()
Game.model_rebuild()
Deck.model_rebuild()
Card.model_rebuild()
UserLink.model_rebuild()
GameLink.model_rebuild()
DeckLink.model_rebuild()
CardLink.model_rebuild()
