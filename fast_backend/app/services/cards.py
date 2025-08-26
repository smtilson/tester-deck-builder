from fast_backend.app.crud.cards import CardManager
from fast_backend.app.crud.decks import DeckManager
from fast_backend.app.crud.deck_cards import DeckCardManager
from fast_backend.app.schemas import CardCreate, CardUpdate, CardResponse
from fast_backend.app.schemas import DeckCreate, DeckUpdate, DeckResponse
from fast_backend.app.schemas import (
    DeckCardCreate,
    DeckCardUpdate,
    # DeckCardResponseWithCard,
)
from fastapi import HTTPException, status


class CardService:
    def __init__(self, card_repo: CardManager):
        self.card_repo = card_repo

    # this should be accepting a different cind of object and it should check that a user has permissions
    def delete_card(self, card_id: int) -> None:
        """
        Delete a card by its ID.

        Args:
            card_id: The ID of the card to delete.
        """
        self.card_repo.delete_card(card_id)
        return None
