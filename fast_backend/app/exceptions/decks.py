from fast_backend.app.models import Deck
from .base import BaseCustomException


class DecksException(BaseCustomException):
    """Base exception for deck related errors"""

    pass


class DeckNotFound(DecksException):

    def __init__(self, deck_id: int):
        self.deck_id = deck_id
        super().__init__(f"Deck with id: {deck_id} not found")
