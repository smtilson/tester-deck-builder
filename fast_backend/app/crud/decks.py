from typing import Optional
from fast_backend.app.models.decks import Deck as DeckModel
from fast_backend.app.schemas.decks import DeckCreate, DeckUpdate, DeckResponse


class DeckRepo:
    @staticmethod
    async def create_deck_record(deck_data: DeckCreate) -> DeckResponse:
        """
        Create a deck.

        Args:
            deck_data: The deck data from the request.

        Returns:
            The created deck as a Pydantic schema instance.
        """
        deck_data_dict = deck_data.model_dump(exclude={"cards"})
        # Assuming owner_id is hardcoded to 1 for now
        deck_obj = await DeckModel.create(**deck_data_dict)
        return DeckResponse.model_validate(deck_obj)

    @staticmethod
    async def get_deck(deck_id: int) -> Optional[DeckResponse]:
        """
        Get a deck by its ID.

        Args:
            deck_id: The ID of the deck to retrieve.

        Returns:
            The deck as a Pydantic schema, or None if it doesn't exist.
        """
        # this response model doesn't have the cards in it.
        deck_obj = await DeckModel.get_or_none(
            id=deck_id
        )  # .prefetch_related("deck_cards__card")
        if deck_obj:
            return DeckResponse.model_validate(deck_obj)
        return None

    @staticmethod
    async def get_all_decks() -> list[DeckResponse]:
        """
        Get all decks.

        Returns:
            A list of all decks as Pydantic schema instances.
        """
        # prefetch owner as well once users are implemented
        # cards are not in this response model
        decks = await DeckModel.all()  # .prefetch_related("deck_cards__card")
        return [DeckResponse.model_validate(deck) for deck in decks]

    @staticmethod
    async def update_deck(
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
        deck_obj = await DeckModel.get_or_none(id=deck_id)
        if deck_obj:
            update_data = deck_data.model_dump(exclude_unset=True)
            if update_data:
                await deck_obj.update_from_dict(update_data).save()
            # Refetch to get the latest state for the response
            await deck_obj.fetch_related("deck_cards__card")
            return DeckResponse.model_validate(deck_obj)
        return None

    @staticmethod
    async def delete_deck(deck_id: int) -> bool:
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
