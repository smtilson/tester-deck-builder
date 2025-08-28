import pytest
import random
from beanie.odm.fields import PydanticObjectId
from pydantic_core import ValidationError

from fast_backend.app.core.exceptions import NotFoundException
from fast_backend.app.models import Card
from fast_backend.app.schemas import CardCreate, CardUpdate, CardResponse

@pytest.mark.skip("standard")
@pytest.mark.asyncio
@pytest.mark.usefixtures("init_db", "cleanup_db")
class TestCardManagerCreate:
    """Integration tests for card_manager create operations."""

    async def test_create_card_success(self, card_manager, setup):
        card_data = setup.data.card
        card_data["game_id"] = setup.data.game["id"]
        card_create = CardCreate(**card_data)
        result = await card_manager.create(card_create)
        assert isinstance(result.id, PydanticObjectId)
        assert result.name == card_data["name"]
        assert result.version == card_data.get("version", "0.0.0")
        assert result.text == card_data.get("text", None)
        assert result.created_at is not None
        assert result.game is not None
        assert result.game.id == card_data["game_id"]
        db_card = await Card.get(result.id)
        assert db_card is not None
        assert db_card.name == card_data["name"]
        assert db_card.text == card_data["text"]

    async def test_create_card_minimal_data(self, card_manager, setup):
        card_create = CardCreate(name="Minimal Card")
        result = await card_manager.create(card_create)
        assert result.name == "Minimal Card"
        assert result.text is None
        assert result.version == "0.0.0"
        assert isinstance(result.id, PydanticObjectId)
        assert result.created_at is not None
        assert result.game is None or result.game.id is None

    async def test_create_multiple_cards_different_names(self, card_manager, setup):
        games = await setup.games()
        card1_data = setup.data.card
        card1_data["game_id"] = random.choice(games).id
        card2_data = setup.data.card
        card2_data["game_id"] = random.choice(games).id
        card1 = CardCreate(**card1_data)
        card2 = CardCreate(**card2_data)
        result1 = await card_manager.create(card1)
        result2 = await card_manager.create(card2)
        assert result1.id != result2.id
        assert result1.name == card1_data["name"]
        assert result2.name == card2_data["name"]
        assert result1.text == card1_data["text"]
        assert result2.text == card2_data["text"]

@pytest.mark.skip("standard")
@pytest.mark.asyncio
@pytest.mark.usefixtures("init_db", "cleanup_db")
class TestCardManagerRead:
    """Integration tests for card_manager read operations."""

    async def test_get_card_by_id_success(self, card_manager, setup):
        cards = await setup.cards()
        created_card = random.choice(cards)
        result = await card_manager.get(created_card.id)
        assert result is not None
        assert isinstance(result.id, PydanticObjectId)
        assert result.id == created_card.id
        assert result.name == created_card.name
        assert result.text == created_card.text
        assert result.version == created_card.version
        _ = {"second":0, "microsecond":0}
        assert result.created_at.replace(**_) == created_card.created_at.replace(**_)
        assert (result.updated_at is None) and (created_card.updated_at is None)
        assert result.game == created_card.game

    async def test_get_card_by_id_not_found(self, card_manager):
        random_id = PydanticObjectId()
        with pytest.raises(NotFoundException) as e:
            await card_manager.get(random_id)
        assert str(random_id) in str(e.value)

    async def test_get_all_cards_returns_all(self, card_manager, setup):
        cards = await setup.cards()
        result = await card_manager.get_all()
        assert len(result) == len(cards)
        card_names = [card.name for card in result]
        expected_names = [card.name for card in cards]
        assert set(card_names) == set(expected_names)
        # Check all fields for each card
        for card, expected in zip(result, cards):
            assert card.id == expected.id
            assert card.name == expected.name
            assert card.text == expected.text
            assert card.version == expected.version
            _ = {"second":0, "microsecond":0}
            assert card.created_at.replace(**_) == expected.created_at.replace(**_)
            assert (card.updated_at is None) and (expected.updated_at is None)
            assert card.game == expected.game

    async def test_get_all_cards_empty_database(self, card_manager):
        await Card.all().delete()
        result = await card_manager.get_all()
        assert result == []

@pytest.mark.skip("standard")
@pytest.mark.asyncio
@pytest.mark.usefixtures("init_db", "cleanup_db")
class TestCardManagerUpdate:
    """Integration tests for CardManager update operations."""

    async def test_update_card_success(self, card_manager, setup):
        cards = await setup.cards()
        single_card = random.choice(cards)
        update_data = CardUpdate(
            name=single_card.name + " updated",
            text=(single_card.text or "") + " updated",
            version="1.2.3"
        )
        result = await card_manager.update(single_card.id, update_data)
        assert result is not None
        assert result.id == single_card.id
        assert result.name == single_card.name + " updated"
        assert result.text == (single_card.text or "") + " updated"
        assert result.version == "1.2.3"
        assert result.updated_at is not None
        db_card = await Card.get(single_card.id)
        assert db_card.name == single_card.name + " updated"
        assert db_card.text == (single_card.text or "") + " updated"
        assert db_card.version == "1.2.3"

    async def test_update_card_partial_update_name_only(self, card_manager, setup):
        cards = await setup.cards()
        single_card = random.choice(cards)
        update_data = CardUpdate(name="Only Name Changed")
        result = await card_manager.update(single_card.id, update_data)
        assert result is not None
        assert result.name == "Only Name Changed"
        assert result.text == single_card.text
        assert result.version == single_card.version
        assert result.id == single_card.id

    async def test_update_card_partial_update_text_only(self, card_manager, setup):
        cards = await setup.cards()
        single_card = random.choice(cards)
        update_data = CardUpdate(text="Only text changed")
        result = await card_manager.update(single_card.id, update_data)
        assert result is not None
        assert result.text == "Only text changed"
        assert result.name == single_card.name
        assert result.version == single_card.version
        assert result.id == single_card.id

    async def test_update_card_partial_update_version_only(self, card_manager, setup):
        cards = await setup.cards()
        single_card = random.choice(cards)
        update_data = CardUpdate(version="2.0.0")
        result = await card_manager.update(single_card.id, update_data)
        assert result is not None
        assert result.version == "2.0.0"
        assert result.name == single_card.name
        assert result.text == single_card.text
        assert result.id == single_card.id

    async def test_update_card_set_text_to_null(self, card_manager, setup):
        cards = await setup.cards()
        single_card = random.choice(cards)
        update_data = CardUpdate(text=None)
        result = await card_manager.update(single_card.id, update_data)
        assert result is not None
        assert result.text is None
        assert result.name == single_card.name
        assert result.version == single_card.version
        assert result.id == single_card.id

    async def test_update_card_set_name_to_null(self, card_manager, setup):
        cards = await setup.cards()
        single_card = random.choice(cards)
        update_data = CardUpdate(name=None)
        with pytest.raises(ValidationError) as e:
            await card_manager.update(single_card.id, update_data)

    async def test_update_card_set_version_to_null(self, card_manager, setup):
        cards = await setup.cards()
        single_card = random.choice(cards)
        update_data = CardUpdate(version=None)
        with pytest.raises(ValidationError) as e:
            await card_manager.update(single_card.id, update_data)

    async def test_update_card_not_found(self, card_manager):
        random_id = PydanticObjectId()
        update_data = CardUpdate(name="New Name")
        with pytest.raises(NotFoundException) as e:
            await card_manager.update(random_id, update_data)
        assert str(random_id) in str(e.value)

@pytest.mark.skip("standard")
@pytest.mark.asyncio
@pytest.mark.usefixtures("init_db", "cleanup_db")
class TestCardManagerDelete:
    """Integration tests for CardManager delete operations."""

    async def test_delete_card_success(self, card_manager):
        card = await card_manager.create(CardCreate(name="Test Card", text="Test Text"))
        id = card.id
        result = await card_manager.delete(id)
        assert result is True

        with pytest.raises(NotFoundException) as e:
            await card_manager.get(id)
        assert str(id) in str(e.value)

        card = await Card.get(id)
        assert card is None

    async def test_delete_card_not_found(self, card_manager):
        random_id = PydanticObjectId()
        with pytest.raises(NotFoundException) as e:
            await card_manager.delete(random_id)
        assert str(random_id) in str(e.value)

    async def test_delete_card_multiple_times(self, card_manager, setup):
        cards = await setup.cards()
        single_card = random.choice(cards)
        id = single_card.id
        result1 = await card_manager.delete(id)
        assert result1 is True

        with pytest.raises(NotFoundException) as e:
            await card_manager.delete(id)
        assert str(id) in str(e.value)

@pytest.mark.skip("special")
@pytest.mark.asyncio
@pytest.mark.usefixtures("init_db", "cleanup_db")
class TestCardManagerEdgeCases:
    """Integration tests for CardManager edge cases and error conditions."""

    async def test_create_card_with_very_long_name(self, card_manager):
        long_name = "A" * 255  # Maximum length according to model
        card_create = CardCreate(name=long_name, text="Test text")
        result = await card_manager.create(card_create)
        assert result.name == long_name
        assert len(result.name) == 255

    async def test_create_card_with_very_long_text(self, card_manager):
        long_text = "This is a very long text. " * 100
        card_create = CardCreate(name="Long Text Card", text=long_text)
        result = await card_manager.create(card_create)
        assert result.text == long_text
        assert result.name == "Long Text Card"

    async def test_create_card_with_empty_text_string(self, card_manager):
        card_create = CardCreate(name="Empty Text Card", text="")
        result = await card_manager.create(card_create)
        assert result.text == ""
        assert result.name == "Empty Text Card"

    async def test_update_nonexistent_card_multiple_times(self, card_manager):
        non_existent_id = PydanticObjectId()
        update_data = CardUpdate(name="Test Name")
        with pytest.raises(NotFoundException):
            await card_manager.update(non_existent_id, update_data)
        with pytest.raises(NotFoundException):
            await card_manager.update(non_existent_id, update_data)

    async def test_card_id_autoincrement(self, card_manager):
        card1 = await card_manager.create(CardCreate(name="Card 1"))
        card2 = await card_manager.create(CardCreate(name="Card 2"))
        card3 = await card_manager.create(CardCreate(name="Card 3"))

        assert card1.id != card2.id != card3.id
        assert card1.id < card2.id < card3.id
