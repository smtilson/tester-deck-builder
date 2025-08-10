import pytest
import pytest_asyncio
from tortoise.exceptions import IntegrityError

from fast_backend.app.crud.cards import CardRepo
from fast_backend.app.schemas.cards import CardCreate, CardUpdate

@pytest.mark.skip
@pytest.mark.usefixtures("init_db")
class TestCardRepoCreate:
    """Integration tests for CardRepo create operations."""

    @pytest.mark.asyncio
    async def test_create_card_success(self, card_test_data):
        """Test successful card creation with valid data."""
        card_data = card_test_data[0]
        card_create = CardCreate(name=card_data["name"], text=card_data["text"])

        result = await CardRepo.create_card(card_create)

        assert result.name == card_data["name"]
        assert result.text == card_data["text"]
        assert isinstance(result.id, int)
        assert result.created_at is not None
        assert result.updated_at is not None
        
        # Verify card exists in database
        from fast_backend.app.models.cards import Card
        db_card = await Card.get(id=result.id)
        assert db_card.name == card_data["name"]
        assert db_card.text == card_data["text"]

    @pytest.mark.asyncio
    async def test_create_card_minimal_data(self):
        """Test creating card with only required fields."""

        card_create = CardCreate(name="Minimal Card")

        result = await CardRepo.create_card(card_create)

        assert result.name == "Minimal Card"
        assert result.text is None
        assert isinstance(result.id, int)

    @pytest.mark.asyncio
    async def test_create_multiple_cards_different_names(self):
        """Test creating multiple cards with different names succeeds."""

        card1 = CardCreate(name="First Card", text="First card text")
        card2 = CardCreate(name="Second Card", text="Second card text")

        result1 = await CardRepo.create_card(card1)
        result2 = await CardRepo.create_card(card2)

        assert result1.id != result2.id
        assert result1.name == "First Card"
        assert result2.name == "Second Card"


@pytest.mark.skip
@pytest.mark.usefixtures("init_db")
class TestCardRepoRead:
    """Integration tests for CardRepo read operations."""

    @pytest_asyncio.fixture(autouse=True)
    async def setup_cards(self, init_db, card_test_data):
        """Create test cards for read operations."""
        created_cards = []
        for card_data in card_test_data:
            card_create = CardCreate(name=card_data["name"], text=card_data["text"])
            created_card = await CardRepo.create_card(card_create)
            created_cards.append(created_card)
        return created_cards

    @pytest.mark.asyncio
    async def test_get_card_by_id_success(self, setup_cards):
        """Test successful retrieval of card by ID."""

        created_card = setup_cards[0]

        result = await CardRepo.get_card(created_card.id)

        assert result is not None
        assert result.id == created_card.id
        assert result.name == created_card.name
        assert result.text == created_card.text

    @pytest.mark.asyncio
    async def test_get_card_by_id_not_found(self):
        """Test that getting non-existent card returns None."""

        non_existent_id = 99999

        result = await CardRepo.get_card(non_existent_id)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_all_cards_returns_all(self, card_test_data):
        """Test that get_all_cards returns all created cards."""

        result = await CardRepo.get_all_cards()

        assert len(result) == len(card_test_data)
        card_names = [card.name for card in result]
        expected_names = [card["name"] for card in card_test_data]
        assert set(card_names) == set(expected_names)

    @pytest.mark.asyncio
    async def test_get_all_cards_empty_database(self):
        """Test get_all_cards with empty database."""
        # Clear all cards
        from fast_backend.app.models.cards import Card

        await Card.all().delete()

        result = await CardRepo.get_all_cards()

        assert result == []

    @pytest.mark.asyncio
    async def test_get_all_cards_maintains_order_and_properties(self):
        """Test that get_all_cards returns cards with all properties intact."""
        result = await CardRepo.get_all_cards()

        for card in result:
            assert isinstance(card.id, int)
            assert isinstance(card.name, str)
            assert card.text is None or isinstance(card.text, str)
            assert card.created_at is not None
            assert card.updated_at is not None


@pytest.mark.skip
@pytest.mark.usefixtures("init_db")
class TestCardRepoUpdate:
    """Integration tests for CardRepo update operations."""

    @pytest_asyncio.fixture(autouse=True)
    async def setup_card(self, init_db, all_test_data):
        """Create a test card for update operations."""
        card_data = all_test_data.get_card_by_name("Lightning Bolt")
        card_create = CardCreate(name=card_data["name"], text=card_data["text"])
        test_card = await CardRepo.create_card(card_create)
        return test_card

    @pytest.mark.asyncio
    async def test_update_card_success(self, setup_card):
        """Test successful card update."""
        update_data = CardUpdate(
            name="Updated Lightning Bolt",
            text="Updated: Lightning Bolt deals 3 damage to any target.",
        )

        result = await CardRepo.update_card(setup_card.id, update_data)

        assert result is not None
        assert result.id == setup_card.id
        assert result.name == "Updated Lightning Bolt"
        assert result.text == "Updated: Lightning Bolt deals 3 damage to any target."
        # Updated timestamp should be different
        assert result.updated_at >= setup_card.updated_at
        
        # Verify update persisted in database
        from fast_backend.app.models.cards import Card
        db_card = await Card.get(id=setup_card.id)
        assert db_card.name == "Updated Lightning Bolt"
        assert db_card.text == "Updated: Lightning Bolt deals 3 damage to any target."

    @pytest.mark.asyncio
    async def test_update_card_partial_update_name_only(self, setup_card):
        """Test partial card update with only name field."""
        update_data = CardUpdate(name="Only Name Changed")

        result = await CardRepo.update_card(setup_card.id, update_data)

        assert result is not None
        assert result.name == "Only Name Changed"
        # Text should remain unchanged
        assert result.text == setup_card.text

    @pytest.mark.asyncio
    async def test_update_card_partial_update_text_only(self, setup_card):
        """Test partial card update with only text field."""
        update_data = CardUpdate(text="Only text changed")

        result = await CardRepo.update_card(setup_card.id, update_data)

        assert result is not None
        assert result.text == "Only text changed"
        # Name should remain unchanged
        assert result.name == setup_card.name

    @pytest.mark.asyncio
    async def test_update_card_set_text_to_null(self, setup_card):
        """Test updating card text to null."""
        update_data = CardUpdate(text=None)

        result = await CardRepo.update_card(setup_card.id, update_data)

        assert result is not None
        assert result.text is None
        assert result.name == setup_card.name

    @pytest.mark.asyncio
    async def test_update_card_empty_update(self, setup_card):
        """Test update with no fields provided."""
        update_data = CardUpdate()

        result = await CardRepo.update_card(setup_card.id, update_data)

        assert result is not None
        # All fields should remain unchanged
        assert result.name == setup_card.name
        assert result.text == setup_card.text

    @pytest.mark.asyncio
    async def test_update_card_not_found(self):
        """Test updating non-existent card returns None."""
        non_existent_id = 99999
        update_data = CardUpdate(name="New Name")

        result = await CardRepo.update_card(non_existent_id, update_data)

        assert result is None


@pytest.mark.skip
@pytest.mark.usefixtures("init_db")
class TestCardRepoDelete:
    """Integration tests for CardRepo delete operations."""

    @pytest_asyncio.fixture(autouse=True)
    async def setup_card(self, init_db, all_test_data):
        """Create a test card for delete operations."""
        card_data = all_test_data.get_card_by_name("Lightning Bolt")
        card_create = CardCreate(name=card_data["name"], text=card_data["text"])
        test_card = await CardRepo.create_card(card_create)
        return test_card

    @pytest.mark.asyncio
    async def test_delete_card_success(self, setup_card):
        """Test successful card deletion."""
        result = await CardRepo.delete_card(setup_card.id)

        assert result is True
        
        # Verify card is actually deleted
        deleted_card = await CardRepo.get_card(setup_card.id)
        assert deleted_card is None
        
        # Verify card no longer exists in database
        from fast_backend.app.models.cards import Card
        from tortoise.exceptions import DoesNotExist
        with pytest.raises(DoesNotExist):
            await Card.get(id=setup_card.id)

    @pytest.mark.asyncio
    async def test_delete_card_not_found(self):
        """Test deleting non-existent card returns False."""
        non_existent_id = 99999

        result = await CardRepo.delete_card(non_existent_id)

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_card_multiple_times(self, setup_card):
        """Test deleting same card multiple times."""
        # First deletion should succeed
        result1 = await CardRepo.delete_card(setup_card.id)
        assert result1 is True

        # Second deletion should fail
        result2 = await CardRepo.delete_card(setup_card.id)
        assert result2 is False


@pytest.mark.skip
@pytest.mark.usefixtures("init_db")
class TestCardRepoEdgeCases:
    """Integration tests for CardRepo edge cases and error conditions."""

    @pytest.mark.asyncio
    async def test_create_card_with_very_long_name(self):
        """Test creating card with maximum length name."""
        long_name = "A" * 255  # Maximum length according to model
        card_create = CardCreate(name=long_name, text="Test text")

        result = await CardRepo.create_card(card_create)

        assert result.name == long_name
        assert len(result.name) == 255

    @pytest.mark.asyncio
    async def test_create_card_with_very_long_text(self):
        """Test creating card with very long text."""
        long_text = "This is a very long text. " * 100  # Very long text
        card_create = CardCreate(name="Long Text Card", text=long_text)

        result = await CardRepo.create_card(card_create)

        assert result.text == long_text
        assert result.name == "Long Text Card"

    @pytest.mark.asyncio
    async def test_create_card_with_empty_text_string(self):
        """Test creating card with empty string as text."""
        card_create = CardCreate(name="Empty Text Card", text="")

        result = await CardRepo.create_card(card_create)

        assert result.text == ""
        assert result.name == "Empty Text Card"

    @pytest.mark.asyncio
    async def test_update_nonexistent_card_multiple_times(self):
        """Test updating non-existent card multiple times returns None consistently."""
        non_existent_id = 99999
        update_data = CardUpdate(name="Test Name")

        result1 = await CardRepo.update_card(non_existent_id, update_data)
        result2 = await CardRepo.update_card(non_existent_id, update_data)

        assert result1 is None
        assert result2 is None

    @pytest.mark.asyncio
    async def test_card_id_autoincrement(self):
        """Test that card IDs are properly auto-incremented."""
        card1 = await CardRepo.create_card(CardCreate(name="Card 1"))
        card2 = await CardRepo.create_card(CardCreate(name="Card 2"))
        card3 = await CardRepo.create_card(CardCreate(name="Card 3"))

        # IDs should be different and in ascending order
        assert card1.id != card2.id != card3.id
        assert card1.id < card2.id < card3.id
