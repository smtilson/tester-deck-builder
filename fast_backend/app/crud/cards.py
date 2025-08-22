from typing import Optional
from fast_backend.app.models.old_cards import Card as CardModel
from fast_backend.app.schemas.cards import CardCreate, CardUpdate, CardResponse


class CardRepo:

    @staticmethod
    async def create_card(card_data: CardCreate) -> CardResponse:
        """
            Create a card.

        Args:
            card_data: The card data from the request

        Returns:
            The created card as a Pydantic schema instance.
        """
        card_obj = await CardModel.create(**card_data.model_dump())
        return CardResponse.model_validate(card_obj)

    @staticmethod
    async def get_card(card_id: int) -> Optional[CardResponse]:
        """
        Get a card by its ID.

        Args:
            card_id: The ID of the card to retrieve

        Returns:
            The card as a Pydantic schema, or None if it doesn't exist.
        """
        card_obj = await CardModel.get_or_none(id=card_id)
        if card_obj:
            return CardResponse.model_validate(card_obj)
        return None

    @staticmethod
    async def get_all_cards() -> list[CardResponse]:
        """
        Get all cards.

        Returns:
            A list of all cards as Pydantic schema instances.
        """
        card_objs = await CardModel.all()
        return [CardResponse.model_validate(card) for card in card_objs]

    @staticmethod
    async def update_card(
        card_id: int, card_data: CardUpdate
    ) -> Optional[CardResponse]:
        """
        Update a card.

        Args:
            card_id: The ID of the card to update
            card_data: The updated card data from the request

        Returns:
            The updated card as a Pydantic schema, or None if the card doesn't exist.
        """
        card_obj = await CardModel.get_or_none(id=card_id)
        if card_obj:
            # Use model_dump(exclude_unset=True) to only get provided fields
            update_data = card_data.model_dump(exclude_unset=True)
            if update_data:  # Only update if there is data
                await card_obj.update_from_dict(update_data).save()
            return CardResponse.model_validate(card_obj)
        return None

    @staticmethod
    async def delete_card(card_id: int) -> bool:
        """
        Delete a card.

        Args:
            card_id: The ID of the card to delete

        Returns:
            True if the card was deleted, False if it doesn't exist
        """
        card_obj = await CardModel.get_or_none(id=card_id)
        if card_obj:
            await card_obj.delete()
            return True
        return False
