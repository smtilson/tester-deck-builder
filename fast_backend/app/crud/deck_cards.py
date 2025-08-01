from typing import Optional

from ..models.deck_cards import DeckCard as DeckCardModel
from ..schemas.deck_cards import (
    DeckCardCreate,
    DeckCardUpdate,
    DeckCardResponseWithCard,
)


class DeckCardRepo:
    @staticmethod
    async def add_card_to_deck(
            deck_id: int, card_data: DeckCardCreate
        ) -> DeckCardResponseWithCard:
        """
        Add a card to a deck. If the card is already in the deck, its quantity is increased.

        Args:
            deck_id: The ID of the deck to add the card to.
            card_data: The data for the link, including card_id and quantity.

        Returns:
            The created or updated DeckCard link as a Pydantic schema.
        """
        link = await DeckCardModel.get_or_none(
            deck_id=deck_id, card_id=card_data.card_id
        )

        if link:
            link.quantity += card_data.quantity
            await link.save()
        else:
            new_link_data = card_data.model_dump()
            new_link_data["deck_id"] = deck_id
            link = await DeckCardModel.create(**new_link_data)

        # Fetch the related card to ensure it's included in the response schema
        await link.fetch_related("card")
        return DeckCardResponseWithCard.model_validate(link)


    @staticmethod
    async def get_cards_for_deck(deck_id: int) -> list[DeckCardResponseWithCard]:
        """
        Get all card links for a specific deck.

        Args:
            deck_id: The ID of the deck.

        Returns:
            A list of DeckCard links as Pydantic schema instances.
        """
        links = await DeckCardModel.filter(deck_id=deck_id).select_related("card")
        return [DeckCardResponseWithCard.model_validate(link) for link in links]


    @staticmethod
    async def update_card_quantity_in_deck(
        deck_card_id: int, deck_card_data: DeckCardUpdate
    ) -> Optional[DeckCardResponseWithCard]:
        """
        Update the quantity of a card in a deck.

        Args:
            deck_card_id: The ID of the DeckCard link itself.
            deck_card_data: The data containing the new quantity.

        Returns:
            The updated DeckCard link as a Pydantic schema, or None if not found.
        """
        deck_card_obj = await DeckCardModel.get_or_none(id=deck_card_id)
        if deck_card_obj:
            update_data = deck_card_data.model_dump(exclude_unset=True)
            if "quantity" in update_data:
                deck_card_obj.quantity = update_data["quantity"]
                await deck_card_obj.save()
            
            await deck_card_obj.fetch_related("card")
            return DeckCardResponseWithCard.model_validate(deck_card_obj)
        return None


    @staticmethod
    async def remove_card_from_deck(deck_card_id: int) -> bool:
        """
        Remove a card from a deck by deleting the DeckCard link.

        Args:
            deck_card_id: The ID of the DeckCard link to delete.

        Returns:
            True if the link was deleted, False otherwise.
        """
        deck_card_obj = await DeckCardModel.get_or_none(id=deck_card_id)
        if deck_card_obj:
            await deck_card_obj.delete()
            return True
        return False
