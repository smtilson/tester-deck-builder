import pytest
import pytest_asyncio
from tortoise.exceptions import DoesNotExist, IntegrityError, ValidationError

from fast_backend.app.models.cards import Card

# The conftest.py provides the `initialize_database` fixture which runs automatically
# for each test, giving us a clean in-memory DB. It also provides the `card_factory`.

@pytest.mark.asyncio
class TestCardModel:
    """
    Test suite for the Card model's database operations (CRUD).
    """
    CARD_DATA = [{"name": f"Card {i}", "text": f"Text {i}"} for i in range(1, 6)]
    
    @pytest.mark.parametrize("card_data", CARD_DATA)
    async def test_create_card(self, card_factory, card_data):
        """Verify that a Card can be created in the database."""
        # Arrange: Use the factory to create the card in the database.
        created_card = await card_factory(card_data)

        # Assert: Check that the returned object has the correct data and an ID.
        assert created_card.id is not None
        assert created_card.name == card_data["name"]
        assert created_card.text == card_data["text"]
        assert created_card.created_at is not None
        assert created_card.updated_at is not None

        # Assert: Verify it exists in the database by fetching it again.
        db_card = await Card.get(id=created_card.id)
        assert db_card is not None
    
    async def test_card_name_is_required(self, card_factory):
        """Verify that a Card cannot be created without a name."""
        # Arrange: Define card data without the 'name' field.
        card_data = {"text": "This card has no name"}

        # Act & Assert: Attempt to create the card and expect an IntegrityError.
        with pytest.raises(ValidationError):
            await card_factory(card_data)
    
    async def test_card_text_is_optional(self, card_factory, card_data):
        """Verify that a Card can be created without text."""
        # Arrange: Define card data without the 'text' field.
        card_data = {"name": "Card without text"}

        # Act: Create the card using the factory.
        created_card = await card_factory(card_data)

        # Assert: Check that the card was created successfully.
        assert created_card.id is not None
        assert created_card.name == card_data["name"]
        assert created_card.text is None

    @pytest.mark.parametrize("card_data", CARD_DATA)
    async def test_read_card(self, card_factory, card_data):
        """Verify that a Card can be read from the database."""
        # Arrange: Create a card to be read.
        created_card = await card_factory(card_data)

        # Act: Fetch the card by its ID.
        read_card = await Card.get(id=created_card.id)

        # Assert: Check that the fetched data is correct.
        assert read_card.id == created_card.id
        assert read_card.name == card_data["name"]
        assert read_card.text == card_data["text"]
    
    @pytest.mark.parametrize("card_data", CARD_DATA)
    async def test_update_card(self, card_factory, card_data):
        """Verify that a Card's attributes can be updated."""
        # Arrange: Create a card.
        card = await card_factory(card_data)
        original_updated_at = card.updated_at

        # Act: Update its text and save it.
        update_data = {key:value+" Update" for key, value in card_data.items()}
        card.name = update_data["name"]
        card.text = update_data["text"]
        await card.save()

        # Assert: Fetch the card again and check if the update was persisted.
        updated_card = await Card.get(id=card.id)
        assert updated_card.name == update_data["name"]
        assert updated_card.text == update_data["text"]
        # Verify the updated_at timestamp has changed.
        assert updated_card.updated_at > original_updated_at
    
    @pytest.mark.parametrize("card_data", CARD_DATA)
    async def test_delete_card(self, card_factory, card_data):
        """Verify that a Card can be deleted from the database."""
        # Arrange: Create a card to be deleted.
        card_to_delete = await card_factory(card_data)
        card_id = card_to_delete.id

        # Confirm it's in the database before deletion.
        assert await Card.all().count() == 1

        # Act: Delete the card.
        await card_to_delete.delete()

        # Assert: Confirm it's no longer in the database.
        assert await Card.all().count() == 0
        with pytest.raises(DoesNotExist):
            await Card.get(id=card_id)