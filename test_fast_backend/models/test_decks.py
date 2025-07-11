import pytest
from tortoise.exceptions import DoesNotExist, IntegrityError

from fast_backend.app.models.decks import Deck

# The conftest.py provides the `initialize_database` fixture (autouse)
# and the `deck_factory`.


@pytest.mark.asyncio
class TestDeckModel:
    """
    Test suite for the Deck model's database operations (CRUD).
    """

    DECK_DATA = [
        {"name": f"Deck {i}", "description": f"Description for Deck {i}"}
        for i in range(1, 4)
    ]

    @pytest.mark.parametrize("deck_data", DECK_DATA)
    async def test_create_deck(self, deck_factory, deck_data):
        """Verify that a Deck can be created in the database."""
        # Arrange: Define the data for the deck.

        # Act: Use the factory to create the deck.
        # The factory automatically handles the owner_id.
        created_deck = await deck_factory(deck_data)

        # Assert: Check that the returned object has the correct data and an ID.
        assert created_deck.id is not None
        assert created_deck.name == deck_data["name"]
        assert created_deck.description == deck_data["description"]
        assert created_deck.is_valid is True
        assert created_deck.owner_id is not None  # Factory should add this
        assert created_deck.created_at is not None
        assert created_deck.updated_at is not None

        # Assert: Verify it exists in the database by fetching it again.
        db_deck = await Deck.get(id=created_deck.id)
        assert db_deck is not None

    async def test_deck_description_is_optional(self, deck_factory, deck_data):
        """Verify that a Deck can be created without a description."""
        # Arrange: Define deck data without the optional 'description' field.
        deck_data = {"name": "No Description Deck"}

        # Act: Create the deck using the factory.
        created_deck = await deck_factory(deck_data)

        # Assert: Check that the description attribute on the object is None.
        assert created_deck.id is not None
        assert created_deck.name == deck_data["name"]
        assert created_deck.description is None

        # Assert: Verify by fetching from the DB that the persisted value is also null.
        db_deck = await Deck.get(id=created_deck.id)
        assert db_deck.description is None

    async def test_deck_name_is_required(self, deck_factory):
        """Verify that creating a Deck without a name raises an error."""
        # Arrange: Define deck data without the required 'name' field.
        deck_data = {"description": "This deck has no name"}

        # Act & Assert: Attempting to create the deck should fail with an
        # IntegrityError because the 'name' column cannot be null.
        with pytest.raises(IntegrityError):
            await deck_factory(deck_data)

    
    @pytest.mark.parametrize("deck_data", DECK_DATA)
    async def test_read_deck(self, deck_factory, deck_data):
        """Verify that a Deck can be read from the database."""
        # Arrange: Create a deck to be read.
        created_deck = await deck_factory(deck_data)

        # Act: Fetch the deck by its ID.
        read_deck = await Deck.get(id=created_deck.id)

        # Assert: Check that the fetched data is correct.
        assert read_deck.id == created_deck.id
        assert read_deck.name == "Burn Deck"
        assert read_deck.description == "All fire spells."
        assert read_deck.is_valid is False  # Should use the model's default

    @pytest.mark.parametrize("deck_data", DECK_DATA)
    async def test_update_deck(self, deck_factory, deck_data):
        """Verify that a Deck's attributes can be updated."""
        # Arrange: Create a deck.
        deck = await deck_factory(deck_data)
        original_updated_at = deck.updated_at

        # Act: Update its attributes and save it.
        update_data = {key: value + " Update" for key, value in deck_data.items()}
        deck.name = update_data["name"]
        deck.description = update_data["description"]
        await deck.save()

        # Assert: Fetch the deck again and check if the updates were persisted.
        updated_deck = await Deck.get(id=deck.id)
        assert updated_deck.name == update_data["name"]
        assert updated_deck.description == update_data["description"]
        assert updated_deck.updated_at > original_updated_at

    @pytest.mark.parametrize("deck_data", DECK_DATA)
    async def test_delete_deck(self, deck_factory, deck_data):
        """Verify that a Deck can be deleted from the database."""
        # Arrange: Create a deck to be deleted.
        deck_to_delete = await deck_factory(deck_data)
        deck_id = deck_to_delete.id

        # Confirm it's in the database before deletion.
        assert await Deck.all().count() == 1

        # Act: Delete the deck.
        await deck_to_delete.delete()

        # Assert: Confirm it's no longer in the database.
        assert await Deck.all().count() == 0
        with pytest.raises(DoesNotExist):
            await Deck.get(id=deck_id)

        """Verify that deck names must be unique."""
        # Arrange: Create a deck with a specific name.
        deck_data = {"name": "Unique Name Deck"}
        await deck_factory(deck_data)

        # Act & Assert: Attempting to create another deck with the same name
        # should raise an IntegrityError (or equivalent for the DB driver).
        with pytest.raises(IntegrityError):
            await deck_factory(deck_data)
