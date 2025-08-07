import pytest
from pydantic import ValidationError

from fast_backend.app.crud.decks import DeckRepo as crud
from fast_backend.app.models.decks import Deck as DeckModel
from fast_backend.app.schemas.decks import DeckCreate, DeckResponse, DeckUpdate

# The conftest.py provides the `initialize_database` fixture (autouse)
# and the `deck_factory`.


@pytest.mark.skip
@pytest.mark.asyncio
@pytest.mark.usefixtures("initialize_database")
class TestDeckCrud:
    """
    Test suite for the Deck CRUD functions.
    """

    DECK_DATA = [
        {"name": f"Deck {i}", "description": f"Description for Deck {i}"}
        for i in range(1, 4)
    ]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("deck_data", DECK_DATA)
    async def test_create_deck(self, initialize_database, deck_data):
        """Verify that crud.create_deck_record correctly creates a deck."""
        # Arrange: Create a Pydantic schema for the new deck.
        deck_to_create = DeckCreate(**deck_data)

        # Act: Call the create_deck CRUD function.
        created_deck = await crud.create_deck_record(deck_to_create)

        # Assert: Check that the returned object is the correct type and has the right data.
        assert isinstance(created_deck, DeckResponse)
        assert created_deck.id is not None
        assert created_deck.name == deck_data["name"]
        assert created_deck.description == deck_data["description"]
        assert created_deck.owner_id == 1  # As hardcoded in the CRUD function

        # Assert: Verify it was actually created in the database.
        db_deck = await DeckModel.get(id=created_deck.id)
        assert db_deck is not None
        assert db_deck.name == deck_data["name"]

    def test_create_deck_validation_error(self):
        """Verify that creating a deck with invalid data raises a ValidationError."""
        # Arrange: Deck data missing the required 'name' field.
        invalid_data = {"description": "This deck has no name"}

        # Act & Assert: Pydantic should raise a validation error on schema creation.
        with pytest.raises(ValidationError):
            DeckCreate(**invalid_data)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("deck_data", DECK_DATA)
    async def test_get_deck(self, initialize_database, deck_factory, deck_data):
        """Verify that crud.get_deck retrieves a deck by its ID."""
        # Arrange: Create a deck in the DB to retrieve.
        db_deck = await deck_factory(deck_data)

        # Act: Retrieve the deck using the CRUD function.
        retrieved_deck = await crud.get_deck(db_deck.id)

        # Assert: Check that the correct deck was returned.
        assert isinstance(retrieved_deck, DeckResponse)
        assert retrieved_deck.id == db_deck.id
        assert retrieved_deck.name == db_deck.name
        assert retrieved_deck.description == db_deck.description

    @pytest.mark.asyncio
    async def test_get_deck_not_found(self, initialize_database):
        """Verify that crud.get_deck returns None for a non-existent ID."""
        # Act: Attempt to retrieve a deck that doesn't exist.
        retrieved_deck = await crud.get_deck(999)

        # Assert: The function should return None.
        assert retrieved_deck is None

    @pytest.mark.asyncio
    async def test_get_all_decks(self, initialize_database, deck_factory):
        """Verify that crud.get_all_decks retrieves all decks."""
        # Arrange: Create multiple decks in the DB.
        for deck_data in self.DECK_DATA:
            await deck_factory(deck_data)

        # Act: Retrieve all decks.
        all_decks = await crud.get_all_decks()

        # Assert: Check that the list contains the correct number of decks.
        assert isinstance(all_decks, list)
        assert len(all_decks) == len(self.DECK_DATA)
        assert all(isinstance(deck, DeckResponse) for deck in all_decks)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("deck_data", DECK_DATA)
    async def test_update_deck(self, initialize_database, deck_factory, deck_data):
        """Verify that crud.update_deck correctly updates a deck."""
        # Arrange: Create a deck to update.
        db_deck = await deck_factory(deck_data)
        update_data = DeckUpdate(name="Updated Name", description="Updated Description")

        # Act: Update the deck using the CRUD function.
        updated_deck = await crud.update_deck(db_deck.id, update_data)

        # Assert: Check that the returned deck has the updated data.
        assert isinstance(updated_deck, DeckResponse)
        assert updated_deck.id == db_deck.id
        assert updated_deck.name == update_data.name
        assert updated_deck.description == update_data.description
        assert updated_deck.updated_at > db_deck.updated_at

        # Assert: Verify the changes were persisted in the database.
        db_deck_after_update = await DeckModel.get(id=db_deck.id)
        assert db_deck_after_update.name == update_data.name
        assert db_deck_after_update.description == update_data.description

    @pytest.mark.asyncio
    async def test_update_deck_not_found(self, initialize_database):
        """Verify that crud.update_deck returns None for a non-existent ID."""
        # Arrange
        update_data = DeckUpdate(name="This will fail")

        # Act
        result = await crud.update_deck(999, update_data)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    @pytest.mark.parametrize("deck_data", DECK_DATA)
    async def test_delete_deck(self, initialize_database, deck_factory, deck_data):
        """Verify that crud.delete_deck correctly deletes a deck."""
        # Arrange: Create a deck to delete.
        db_deck = await deck_factory(deck_data)
        assert await DeckModel.all().count() == 1

        # Act: Delete the deck using the CRUD function.
        result = await crud.delete_deck(db_deck.id)

        # Assert: Check that the function returned True and the deck is gone.
        assert result is True
        assert await DeckModel.all().count() == 0
        assert await DeckModel.get_or_none(id=db_deck.id) is None

    @pytest.mark.asyncio
    async def test_delete_deck_not_found(self, initialize_database):
        """Verify that crud.delete_deck returns False for a non-existent ID."""
        # Act
        result = await crud.delete_deck(999)

        # Assert
        assert result is False
