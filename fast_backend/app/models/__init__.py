"""
Database models using Beanie ODM.
"""

from .users import User, get_user_db
from .cards import Card
from .decks import Deck
from .deck_cards import DeckCard
from .games import Game
from .base import BaseDocument

__all__ = ["User", "Card", "Deck", "DeckCard", "Game", "BaseDocument", "get_user_db"]

User.model_rebuild() 
Game.model_rebuild()