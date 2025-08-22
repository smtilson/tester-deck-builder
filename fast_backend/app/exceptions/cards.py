from fast_backend.app.models.cards import Card

# should we have any of these schemas
from fast_backend.app.schemas.cards import CardResponse
from .base import BaseCustomException


class CardsException(BaseCustomException):
    """Exception for cards"""

    pass


class CardsNotFound(CardsException):
    """Exception raised when a card is not found"""

    def __init__(self, card_ids: list[int]):
        self.card_ids = card_ids
        if len(card_ids) == 1:
            super().__init__(f"Card with id: {card_ids[0]} not found")
        else:
            super().__init__(f"Cards with ids: {card_ids} not found")
