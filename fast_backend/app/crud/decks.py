from typing import Optional
from fast_backend.app.models.decks import Deck as DeckModel
from fast_backend.app.models.users import User as UserModel
from fast_backend.app.schemas.decks import (
    DeckBase,
    DeckCreate,
    DeckUpdate,
    DeckResponse,
)

from fast_backend.app.crud.base_manager import BaseManager

class DeckManager(BaseManager[DeckModel, DeckCreate, DeckUpdate, DeckResponse]):
    pass

deck_manager = DeckManager(doc_model=DeckModel, response_schema=DeckResponse)


# I think this can be refactored into a base class pattern.
class OldDeckManager:
    @staticmethod
    async def create(deck_data: DeckCreate) -> DeckResponse:
        """
        Create a deck.

        Args:
            deck_data: The deck data from the request.

        Returns:
            The created deck as a Pydantic schema instance.
        """
        deck_data_dict = deck_data.model_dump(exclude={"cards", "owner"})
        deck_data_dict["owner"] = await DeckManager.get_owner_in_db(deck_data)
        deck_obj = await DeckModel.create(**deck_data_dict)
        return DeckResponse.model_validate(deck_obj)

    @staticmethod
    async def get(deck_id: int) -> Optional[DeckResponse]:
        """
        Get a deck by its ID.

        Args:
            deck_id: The ID of the deck to retrieve.

        Returns:
            The deck as a Pydantic schema, or None if it doesn't exist.
        """
        # this response model doesn't have the cards in it.
        deck_obj = await DeckModel.get_or_none(id=deck_id).prefetch_related(
            "owner"
        )  # .prefetch_related("deck_cards__card")
        if deck_obj:
            return DeckResponse.model_validate(deck_obj)
        return None

    @staticmethod
    async def get_all() -> list[DeckResponse]:
        """
        Get all decks.

        Returns:
            A list of all decks as Pydantic schema instances.
        """
        # prefetch owner as well once users are implemented
        # cards are not in this response model
        decks = await DeckModel.all().prefetch_related(
            "owner"
        )  # .prefetch_related("deck_cards__card")
        return [DeckResponse.model_validate(deck) for deck in decks]

    @staticmethod
    async def get_owner_in_db(deck_data: DeckBase) -> Optional[UserModel]:
        """
        Get the owner of a deck.

        Args:
            deck_data: The deck data containing owner information.

        Returns:
            The owner as a UserModel instance, or None if not found.
        """
        owner = await UserModel.get_or_none(id=deck_data.owner.id)
        if not owner:
            raise ValueError(
                f"User with id: {deck_data.owner.id} does not exist. Deck has no valid owner."
            )
        return owner

    @staticmethod
    async def update(
        deck_id: int, deck_data: DeckUpdate
    ) -> Optional[DeckResponse]:
        """
        Update a deck.

        Args:
            deck_id: The ID of the deck to update.
            deck_data: The updated deck data from the request.

        Returns:
            The updated deck as a Pydantic schema, or None if the deck doesn't exist.
        """
        deck_in_db = await DeckModel.get_or_none(id=deck_id).prefetch_related("owner")
        if not deck_in_db:
            return None
        update_data = deck_data.model_dump(exclude_unset=True, exclude={"owner"})
        if not update_data:
            return DeckResponse.model_validate(deck_in_db)
        if deck_data.owner:
            update_data["owner"] = await UserModel.get(id=deck_data.owner.id)
        else:
            update_data["owner"] = deck_in_db.owner
        await deck_in_db.update_from_dict(update_data).save()
        return DeckResponse.model_validate(deck_in_db)

    @staticmethod
    async def delete(deck_id: int) -> bool:
        """
        Delete a deck.

        Args:
            deck_id: The ID of the deck to delete.

        Returns:
            True if the deck was deleted, False if it doesn't exist.
        """
        deck_obj = await DeckModel.get_or_none(id=deck_id)
        if deck_obj:
            await deck_obj.delete()
            return True
        return False
