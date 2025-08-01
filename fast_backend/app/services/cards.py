from app.crud.cards import CardRepo
from app.crud.decks import DeckRepo
from app.crud.deck_cards import DeckCardRepo
from app.schemas.cards import CardCreate, CardUpdate, CardResponse
from app.schemas.decks import DeckCreate, DeckUpdate, DeckResponse
from app.schemas.deck_cards import DeckCardCreate, DeckCardUpdate, DeckCardResponseWithCard
from fastapi import HTTPException, status

class CardService:
    def __init__(self, card_repo: CardRepo):
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