"""Tests for Deck model CRUD operations."""

import pytest
from tortoise.exceptions import DoesNotExist, ValidationError, IntegrityError

from fast_backend.app.models.decks import Deck
from fast_backend.app.models.users import User
from test_fast_backend.conftest import SAMPLE_DECKS


#@pytest.mark.skip("standard")
@pytest.mark.asyncio
@pytest.mark.usefixtures("initialize_database")
class TestDeckModel:
    """Test suite for Deck model database operations."""

    @pytest.mark.parametrize("deck_data", SAMPLE_DECKS)
    async def test_create_deck(self, deck_factory, deck_data):
        """Verify that a Deck can be created in the database."""

        created_deck = await deck_factory(deck_data)

        assert created_deck.id is not None
        assert created_deck.name == deck_data["name"]
        assert created_deck.description == deck_data["description"]
        assert created_deck.is_valid is False  # Default value
        assert created_deck.owner_id is not None
        assert created_deck.created_at is not None
        assert created_deck.updated_at is not None

        # Verify it exists in the database
        db_deck = await Deck.get(id=created_deck.id)
        assert db_deck is not None
    @pytest.mark.skip("standard")
    async def test_deck_description_is_optional(self, deck_factory):
        """Verify that a Deck can be created without a description."""
        deck_data = {"name": "No Description Deck"}

        created_deck = await deck_factory(deck_data)

        assert created_deck.id is not None
        assert created_deck.name == deck_data["name"]
        assert created_deck.description is None

        # Verify in database
        db_deck = await Deck.get(id=created_deck.id)
        assert db_deck.description is None
    @pytest.mark.skip("standard")
    async def test_deck_name_is_required(self, deck_factory):
        """Verify that creating a Deck without a name raises an error."""
        deck_data = {"description": "This deck has no name"}

        with pytest.raises(ValidationError):
            await deck_factory(deck_data)
    @pytest.mark.skip("standard")
    @pytest.mark.parametrize("deck_data", SAMPLE_DECKS)
    async def test_read_deck(self, deck_factory, deck_data):
        """Verify that a Deck can be read from the database."""
        created_deck = await deck_factory(deck_data)

        read_deck = await Deck.get(id=created_deck.id)

        assert read_deck.id == created_deck.id
        assert read_deck.name == deck_data["name"]
        assert read_deck.description == deck_data["description"]
        assert read_deck.is_valid is False
    @pytest.mark.skip("standard")
    @pytest.mark.parametrize("deck_data", SAMPLE_DECKS)
    async def test_update_deck(self, deck_factory, deck_data):
        """Verify that a Deck's attributes can be updated."""
        deck = await deck_factory(deck_data)
        original_updated_at = deck.updated_at

        # Update the deck
        new_name = deck_data["name"] + " Updated"
        new_description = deck_data["description"] + " Updated"
        deck.name = new_name
        deck.description = new_description
        await deck.save()

        # Verify the update was persisted
        updated_deck = await Deck.get(id=deck.id)
        assert updated_deck.name == new_name
        assert updated_deck.description == new_description
        assert updated_deck.updated_at > original_updated_at
    @pytest.mark.skip("standard")
    @pytest.mark.parametrize("deck_data", SAMPLE_DECKS)
    async def test_delete_deck(self, deck_factory, deck_data):
        """Verify that a Deck can be deleted from the database."""
        deck_to_delete = await deck_factory(deck_data)
        deck_id = deck_to_delete.id

        # Confirm it exists before deletion
        assert await Deck.all().count() == 1

        # Delete the deck
        await deck_to_delete.delete()

        # Confirm it's no longer in the database
        assert await Deck.all().count() == 0
        with pytest.raises(DoesNotExist):
            await Deck.get(id=deck_id)
    @pytest.mark.skip("standard")
    async def test_deck_name_uniqueness(self, deck_factory):
        """Verify that deck names must be unique."""
        deck_data = {"name": "Unique Name Deck"}
        await deck_factory(deck_data)

        # Attempting to create another deck with the same name should fail
        with pytest.raises(IntegrityError):
            await deck_factory(deck_data)
