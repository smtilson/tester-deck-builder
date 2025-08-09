"""Tests for Card model CRUD operations."""

import pytest
from tortoise.exceptions import DoesNotExist, ValidationError

from fast_backend.app.models.cards import Card
from test_fast_backend.conftest import SAMPLE_CARDS


@pytest.mark.skip("standard")
@pytest.mark.asyncio
@pytest.mark.usefixtures("initialize_database")
class TestCardModel:
    """Test suite for Card model database operations."""

    @pytest.mark.parametrize("card_data", SAMPLE_CARDS)
    async def test_create_card(self, card_factory, card_data):
        """Verify that a Card can be created in the database."""
        created_card = await card_factory(card_data)

        assert created_card.id is not None
        assert created_card.name == card_data["name"]
        assert created_card.text == card_data["text"]
        assert created_card.created_at is not None
        assert created_card.updated_at is not None

        # Verify it exists in the database
        db_card = await Card.get(id=created_card.id)
        assert db_card is not None

    async def test_card_name_is_required(self, card_factory):
        """Verify that a Card cannot be created without a name."""
        card_data = {"text": "This card has no name"}

        with pytest.raises(ValidationError):
            await card_factory(card_data)

    async def test_card_text_is_optional(self, card_factory):
        """Verify that a Card can be created without text."""
        card_data = {"name": "Card without text"}

        created_card = await card_factory(card_data)

        assert created_card.id is not None
        assert created_card.name == card_data["name"]
        assert created_card.text is None

    @pytest.mark.parametrize("card_data", SAMPLE_CARDS)
    async def test_read_card(self, card_factory, card_data):
        """Verify that a Card can be read from the database."""
        created_card = await card_factory(card_data)

        read_card = await Card.get(id=created_card.id)

        assert read_card.id == created_card.id
        assert read_card.name == card_data["name"]
        assert read_card.text == card_data["text"]

    @pytest.mark.parametrize("card_data", SAMPLE_CARDS)
    async def test_update_card(self, card_factory, card_data):
        """Verify that a Card's attributes can be updated."""
        card = await card_factory(card_data)
        original_updated_at = card.updated_at

        # Update the card
        new_name = card_data["name"] + " Updated"
        new_text = card_data["text"] + " Updated"
        card.name = new_name
        card.text = new_text
        await card.save()

        # Verify the update was persisted
        updated_card = await Card.get(id=card.id)
        assert updated_card.name == new_name
        assert updated_card.text == new_text
        assert updated_card.updated_at > original_updated_at

    @pytest.mark.parametrize("card_data", SAMPLE_CARDS)
    async def test_delete_card(self, card_factory, card_data):
        """Verify that a Card can be deleted from the database."""
        card_to_delete = await card_factory(card_data)
        card_id = card_to_delete.id

        # Confirm it exists before deletion
        assert await Card.all().count() == 1

        # Delete the card
        await card_to_delete.delete()

        # Confirm it's no longer in the database
        assert await Card.all().count() == 0
        with pytest.raises(DoesNotExist):
            await Card.get(id=card_id)
