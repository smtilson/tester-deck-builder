import pytest
import random
from beanie.odm.fields import PydanticObjectId

from fast_backend.app.crud.cards import CardRepo
from fast_backend.app.models.cards import Card
from fast_backend.app.schemas.cards import CardCreate, CardUpdate


# @pytest.mark.skip("standard")
@pytest.mark.asyncio
@pytest.mark.usefixtures("init_db")
class TestCardRepoCreate:
    """Integration tests for CardRepo create operations."""

    async def test_create_card_success(self, card_test_data):
        """Test successful card creation with valid data."""
        card_data = random.choice(card_test_data)
        card_create = CardCreate(**card_data)

        result = await CardRepo.create_card(card_create)

        assert result.name == card_data["name"]
        assert result.text == card_data["text"]
        assert isinstance(result.id, PydanticObjectId)
        assert result.created_at is not None
        assert result.updated_at is None

        # Verify card exists in database
        db_card = await Card.get(result.id)
        assert db_card.name == card_data["name"]
        assert db_card.text == card_data["text"]

    async def test_create_card_minimal_data(self):
        """Test creating card with only required fields."""

        card_create = CardCreate(name="Minimal Card")

        result = await CardRepo.create_card(card_create)

        assert result.name == "Minimal Card"
        assert result.text is None
        assert isinstance(result.id, PydanticObjectId)

    async def test_create_multiple_cards_different_names(self):
        """Test creating multiple cards with different names succeeds."""

        card1 = CardCreate(name="First Card", text="First card text")
        card2 = CardCreate(name="Second Card", text="Second card text")

        result1 = await CardRepo.create_card(card1)
        result2 = await CardRepo.create_card(card2)

        assert result1.id != result2.id
        assert result1.name == "First Card"
        assert result2.name == "Second Card"


@pytest.mark.skip("standard")
@pytest.mark.asyncio
@pytest.mark.usefixtures("init_db")
class TestCardRepoRead:
    """Integration tests for CardRepo read operations."""

    async def test_get_card_by_id_success(self, setup_cards):
        """Test successful retrieval of card by ID."""

        created_card = random.choice(setup_cards)

        result = await CardRepo.get_card(created_card.id)

        assert result is not None
        assert result.id == created_card.id
        assert result.name == created_card.name
        assert result.text == created_card.text

    async def test_get_card_by_id_not_found(self, setup_cards):
        """Test that getting non-existent card returns None."""

        random_id = random.randint(1000, 9999)  # Assuming this ID does not exist
        while random_id in [card.id for card in setup_cards]:
            random_id = random.randint(1000, 9999)

        result = await CardRepo.get_card(random_id)

        assert result is None

    async def test_get_all_cards_returns_all(self, setup_cards):
        """Test that get_all_cards returns all created cards."""

        result = await CardRepo.get_all_cards()

        assert len(result) == len(setup_cards)
        card_names = [card.name for card in result]
        expected_names = [card.name for card in setup_cards]
        assert set(card_names) == set(expected_names)

    async def test_get_all_cards_empty_database(self):
        """Test get_all_cards with empty database."""
        # Clear all cards

        await Card.all().delete()

        result = await CardRepo.get_all_cards()

        assert result == []


@pytest.mark.skip("standard")
@pytest.mark.asyncio
@pytest.mark.usefixtures("init_db")
class TestCardRepoUpdate:
    """Integration tests for CardRepo update operations."""

    async def test_update_card_success(self, single_card):
        """Test successful card update."""
        update_data = CardUpdate(
            name=single_card.name + " updated",
            text=single_card.text + " updated",
        )

        result = await CardRepo.update_card(single_card.id, update_data)

        assert result is not None
        assert result.id == single_card.id
        assert result.name == single_card.name + " updated"
        assert result.text == single_card.text + " updated"
        # Updated timestamp should be different
        assert result.updated_at >= single_card.updated_at

        # Verify update persisted in database
        db_card = await Card.get(id=single_card.id)
        assert db_card.name == single_card.name + " updated"
        assert db_card.text == single_card.text + " updated"

    async def test_update_card_partial_update_name_only(self, single_card):
        """Test partial card update with only name field."""
        update_data = CardUpdate(name="Only Name Changed")

        result = await CardRepo.update_card(single_card.id, update_data)

        assert result is not None
        assert result.name == "Only Name Changed"
        # Text should remain unchanged
        assert result.text == single_card.text
        assert result.id == single_card.id

    async def test_update_card_partial_update_text_only(self, single_card):
        """Test partial card update with only text field."""
        update_data = CardUpdate(text="Only text changed")

        result = await CardRepo.update_card(single_card.id, update_data)

        assert result is not None
        assert result.text == "Only text changed"
        # Name should remain unchanged
        assert result.name == single_card.name
        assert result.id == single_card.id

    async def test_update_card_set_text_to_null(self, single_card):
        """Test updating card text to null."""
        update_data = CardUpdate(text=None)

        result = await CardRepo.update_card(single_card.id, update_data)

        assert result is not None
        assert result.text is None
        assert result.name == single_card.name
        assert result.id == single_card.id

    async def test_update_card_empty_update(self, single_card):
        """Test update with no fields provided."""
        update_data = CardUpdate()

        result = await CardRepo.update_card(single_card.id, update_data)

        assert result is not None
        # All fields should remain unchanged
        assert result.name == single_card.name
        assert result.text == single_card.text
        assert result.id == single_card.id

    async def test_update_card_not_found(self):
        """Test updating non-existent card returns None."""
        non_existent_id = random.randint(1000, 99999)
        existing_ids = [card.id for card in await CardRepo.get_all_cards()]
        while non_existent_id in existing_ids:
            non_existent_id = random.randint(1000, 99999)
        update_data = CardUpdate(name="New Name")

        result = await CardRepo.update_card(non_existent_id, update_data)

        assert result is None


@pytest.mark.skip("standard")
@pytest.mark.asyncio
@pytest.mark.usefixtures("init_db")
class TestCardRepoDelete:
    """Integration tests for CardRepo delete operations."""

    async def test_delete_card_success(self, single_card):
        """Test successful card deletion."""
        result = await CardRepo.delete_card(single_card.id)

        assert result is True

        # Verify card is actually deleted
        deleted_card = await CardRepo.get_card(single_card.id)
        assert deleted_card is None

        # Verify card no longer exists in database
        with pytest.raises(DoesNotExist):
            await Card.get(id=single_card.id)

    async def test_delete_card_not_found(self):
        """Test deleting non-existent card returns False."""
        non_existent_id = random.randint(1000, 99999)
        existing_ids = [card.id for card in await CardRepo.get_all_cards()]
        while non_existent_id in existing_ids:
            non_existent_id = random.randint(1000, 99999)

        result = await CardRepo.delete_card(non_existent_id)

        assert result is False

    async def test_delete_card_multiple_times(self, single_card):
        """Test deleting same card multiple times."""
        # First deletion should succeed
        result1 = await CardRepo.delete_card(single_card.id)
        assert result1 is True

        # Second deletion should fail
        result2 = await CardRepo.delete_card(single_card.id)
        assert result2 is False


@pytest.mark.skip("special")
@pytest.mark.asyncio
@pytest.mark.usefixtures("init_db")
class TestCardRepoEdgeCases:
    """Integration tests for CardRepo edge cases and error conditions."""

    async def test_create_card_with_very_long_name(self):
        """Test creating card with maximum length name."""
        long_name = "A" * 255  # Maximum length according to model
        card_create = CardCreate(name=long_name, text="Test text")

        result = await CardRepo.create_card(card_create)

        assert result.name == long_name
        assert len(result.name) == 255

    async def test_create_card_with_very_long_text(self):
        """Test creating card with very long text."""
        long_text = "This is a very long text. " * 100  # Very long text
        card_create = CardCreate(name="Long Text Card", text=long_text)

        result = await CardRepo.create_card(card_create)

        assert result.text == long_text
        assert result.name == "Long Text Card"

    async def test_create_card_with_empty_text_string(self):
        """Test creating card with empty string as text."""
        card_create = CardCreate(name="Empty Text Card", text="")

        result = await CardRepo.create_card(card_create)

        assert result.text == ""
        assert result.name == "Empty Text Card"

    async def test_update_nonexistent_card_multiple_times(self):
        """Test updating non-existent card multiple times returns None consistently."""
        non_existent_id = 99999
        update_data = CardUpdate(name="Test Name")

        result1 = await CardRepo.update_card(non_existent_id, update_data)
        result2 = await CardRepo.update_card(non_existent_id, update_data)

        assert result1 is None
        assert result2 is None

    async def test_card_id_autoincrement(self):
        """Test that card IDs are properly auto-incremented."""
        card1 = await CardRepo.create_card(CardCreate(name="Card 1"))
        card2 = await CardRepo.create_card(CardCreate(name="Card 2"))
        card3 = await CardRepo.create_card(CardCreate(name="Card 3"))

        # IDs should be different and in ascending order
        assert card1.id != card2.id != card3.id
        assert card1.id < card2.id < card3.id
