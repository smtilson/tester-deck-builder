from typing import Optional
from beanie.odm.fields import PydanticObjectId
from datetime import datetime

from fast_backend.app.models.cards import Card as CardModel
from fast_backend.app.schemas.cards import CardCreate, CardUpdate, CardResponse
from fast_backend.app.core.exceptions import NotFoundException
from fast_backend.app.crud.base_manager import BaseManager


class CardManager(BaseManager[CardModel, CardCreate, CardUpdate, CardResponse]):
    pass

card_manager = CardManager(doc_model=CardModel, response_schema=CardResponse)
class OldCardManager:

    @staticmethod
    async def create(card_in: CardCreate) -> CardResponse:
        """
            Create a card.

        Args:
            card_data: The card data from the request

        Returns:
            The created card as a Pydantic schema instance.
        """
        card_obj = CardModel(**card_in.model_dump())
        await card_obj.insert()
        return CardResponse.model_validate(card_obj)

    @staticmethod
    async def get_model(card_id: PydanticObjectId) -> CardModel:
        """
        Get a card by its ID.

        Args:
            card_id: The ID of the card to retrieve

        Returns:
            The card as a Pydantic schema, or None if it doesn't exist.
        """
        print("get_model called")
        card_model = await CardModel.get(card_id)
        if not card_model:
            print("record not found")
            raise NotFoundException(f"No Card with ID {card_id} was found.")
        print("record found")
        print("exiting get_model")
        return card_model

    @staticmethod
    async def get(card_id: PydanticObjectId) -> Optional[CardResponse]:
        """
        Get a card by its ID.

        Args:
            card_id: The ID of the card to retrieve

        Returns:
            The card as a Pydantic schema, or None if it doesn't exist.
        """
        print("get_card called")
        card_obj = await CardManager.get_model(card_id)
        print("card model found.")
        print("converting to CardResponse and exiting get card")
        return CardResponse.model_validate(card_obj)

    @staticmethod
    async def get_all() -> list[CardResponse]:
        """
        Get all cards.

        Returns:
            A list of all cards as Pydantic schema instances.
        """
        card_objs = await CardModel.find_all().to_list()
        return [CardResponse.model_validate(card) for card in card_objs]

    @staticmethod
    async def update(
        card_id: PydanticObjectId, card_data: CardUpdate
    ) -> Optional[CardResponse]:
        """
        Update a card.

        Args:
            card_id: The ID of the card to update
            card_data: The updated card data from the request

        Returns:
            The updated card as a Pydantic schema, or None if the card doesn't exist.
        """
        card_obj = await CardManager.get_model(card_id)
        update_data = card_data.model_dump(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.now()
            await card_obj.set(update_data)
            await card_obj.save()
        return CardResponse.model_validate(card_obj)

    @staticmethod
    async def delete(card_id: PydanticObjectId) -> bool:
        """
        Delete a card.

        Args:
            card_id: The ID of the card to delete

        Returns:
            True if the card was deleted, False if it doesn't exist
        """
        print("delete card called")
        card_obj = await CardManager.get_model(card_id)
        print("card found for deletion")
        await card_obj.delete()
        print("card deleted")
        return True
