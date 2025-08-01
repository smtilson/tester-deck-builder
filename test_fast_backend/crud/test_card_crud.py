"""Tests for Card CRUD operations."""

import pytest
from pydantic import ValidationError

from fast_backend.app.crud.cards import CardRepo as crud
from fast_backend.app.models.cards import Card as CardModel
from fast_backend.app.schemas.cards import CardCreate, CardResponse, CardUpdate
from test_fast_backend.conftest import SAMPLE_CARDS


# # @pytest.mark.skip
@pytest.mark.asyncio
class TestCardCrud:
    """Test suite for Card CRUD functions."""

    @pytest.mark.parametrize("card_data", SAMPLE_CARDS)
    async def test_create_card(self, card_data):
        """Verify that crud.create_card correctly creates a card."""
        card_to_create = CardCreate(**card_data)

        created_card = await crud.create_card(card_to_create)

        assert isinstance(created_card, CardResponse)
        assert created_card.id is not None
        assert created_card.name == card_data["name"]
        assert created_card.text == card_data["text"]

        # Verify it was actually created in the database
        db_card = await CardModel.get(id=created_card.id)
        assert db_card is not None
        assert db_card.name == card_data["name"]
        assert db_card.text == card_data["text"]

    def test_create_card_validation_error(self):
        """Verify that creating a card with invalid data raises a ValidationError."""
        invalid_data = {"text": "This card has no name"}

        with pytest.raises(ValidationError):
            CardCreate(**invalid_data)

    @pytest.mark.parametrize("card_data", SAMPLE_CARDS)
    async def test_get_card(self, card_factory, card_data):
        """Verify that crud.get_card retrieves a card by its ID."""
        db_card = await card_factory(card_data)

        retrieved_card = await crud.get_card(db_card.id)

        assert isinstance(retrieved_card, CardResponse)
        assert retrieved_card.id == db_card.id
        assert retrieved_card.name == db_card.name
        assert retrieved_card.text == db_card.text

    async def test_get_card_not_found(self):
        """Verify that crud.get_card returns None for a non-existent ID."""
        retrieved_card = await crud.get_card(999)

        assert retrieved_card is None

    async def test_get_all_cards(self, card_factory):
        """Verify that crud.get_all_cards retrieves all cards."""
        # Create multiple cards
        for card_data in SAMPLE_CARDS:
            await card_factory(card_data)

        all_cards = await crud.get_all_cards()

        assert isinstance(all_cards, list)
        assert len(all_cards) == len(SAMPLE_CARDS)
        assert all(isinstance(card, CardResponse) for card in all_cards)

    @pytest.mark.parametrize("card_data", SAMPLE_CARDS)
    async def test_update_card(self, card_factory, card_data):
        """Verify that crud.update_card correctly updates a card."""
        db_card = await card_factory(card_data)
        update_data = CardUpdate(name="Updated Name", text="Updated Text")

        updated_card = await crud.update_card(db_card.id, update_data)

        assert isinstance(updated_card, CardResponse)
        assert updated_card.id == db_card.id
        assert updated_card.name == update_data.name
        assert updated_card.text == update_data.text
        assert updated_card.updated_at > db_card.updated_at

        # Verify the changes were persisted in the database
        db_card_after_update = await CardModel.get(id=db_card.id)
        assert db_card_after_update.name == update_data.name
        assert db_card_after_update.text == update_data.text

    async def test_update_card_not_found(self):
        """Verify that crud.update_card returns None for a non-existent ID."""
        update_data = CardUpdate(name="This will fail")

        result = await crud.update_card(999, update_data)

        assert result is None

    @pytest.mark.parametrize("card_data", SAMPLE_CARDS)
    async def test_delete_card(self, card_factory, card_data):
        """Verify that crud.delete_card correctly deletes a card."""
        db_card = await card_factory(card_data)
        assert await CardModel.all().count() == 1

        result = await crud.delete_card(db_card.id)

        assert result is True
        assert await CardModel.all().count() == 0
        assert await CardModel.get_or_none(id=db_card.id) is None

    async def test_delete_card_not_found(self):
        """Verify that crud.delete_card returns False for a non-existent ID."""
        result = await crud.delete_card(999)

        assert result is False
