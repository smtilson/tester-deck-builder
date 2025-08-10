from collections import defaultdict

from fastapi import HttpException, status
from tortoise.transactions import atomic

from fast_backend.app.schemas.cards import CardInDB
from fast_backend.app.schemas.deck_cards import DeckCardCreate
from fast_backend.app.models.deck_cards import DeckCard as DeckCardModel
from fast_backend.app.models.decks import Deck as DeckModel

from fast_backend.app.exceptions.cards import CardsNotFound
from fast_backend.app.exceptions.decks import DeckNotFound, DeckException


class DeckCardService:

    @staticmethod
    async def get_deck_by_id(deck_id: int):
        """Fetch a deck by its ID."""
        deck = await DeckModel.get_or_none(id=deck_id)
        if not deck:
            raise DeckNotFound(deck_id)
        return deck

    @staticmethod
    def add_quantities(card_data: list[int, int]):
        """Add quantities of cards to a deck."""
        combined_data = defaultdict(int)
        for id, quantity in card_data:
            combined_data[id] += quantity
        return list(combined_data.items())

    @staticmethod
    def same_deck(cards_to_add: list[DeckCardCreate]):
        """Check if all cards belong to the same deck."""
        deck_ids = list({card.deck_id for card in cards_to_add})
        if len(deck_ids) > 1:
            return DeckException("You can only add cards to one deck at a time."), None
        return deck_ids[0]

    @staticmethod
    async def process_add_cards_request(cards_to_add: list[DeckCardCreate]):
        """Process the request to add cards to a deck."""
        deck_id = DeckCardService.same_deck(cards_to_add)
        card_data = [(datum.card_id, datum.quantity) for datum in cards_to_add]
        card_data = DeckCardService.add_quantities(card_data)
        card_ids = [card[0] for card in card_data]
        missing_ids = await DeckCardService.find_cards_by_ids(card_ids)
        if missing_ids:
            raise CardsNotFound(missing_ids)
        processed_data = [
            {"deck_id": deck_id, "card_id": card[0], "quantity": card[1]}
            for card in card_data
        ]
        processed_data = [DeckCardCreate(**data) for data in processed_data]
        return processed_data

    @staticmethod
    async def find_cards_by_ids(card_ids: list[int]):
        """Find any missing card IDs."""
        card_ids = set(card_ids)
        # maybe I can not
        found_cards = await CardInDB.filter(id__in=card_ids)
        missing_ids = card_ids - {card.id for card in found_cards}
        return missing_ids
