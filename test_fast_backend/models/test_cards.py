import pytest
from beanie import PydanticObjectId, Link
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from pydantic import ValidationError

from fast_backend.app.models import Card, CardLink, Game, GameLink
from fast_backend.app.schemas import CardListItem, GameListItem


@pytest.mark.skip("standard")
@pytest.mark.usefixtures("init_db", "cleanup_db")
@pytest.mark.asyncio
class TestCardModelCreate:
    async def test_create_card_success(self, data):
        card_data = data.card
        card = Card(**card_data)
        await card.insert()
        assert isinstance(card.id, PydanticObjectId)
        assert card.name == card_data["name"]
        assert card.text == card_data["text"]
        assert card.version is not None
        assert isinstance(card.created_at, datetime)

        db_card = await Card.get(card.id)
        assert db_card is not None
        assert db_card.name == card.name
        assert db_card.text == card.text
        assert db_card.version == card.version

    async def test_create_card_duplicate_name_version_fails(self, data):
        card_data = data.card
        card_data["version"] = card_data.get("version", "1.0.0")
        card_data["created_at"] = datetime.now()
        card1 = Card(**card_data)
        await card1.insert()
        card2_data = card_data.copy()
        card2_data["text"] = "Another card"
        card2 = Card(**card2_data)
        with pytest.raises(DuplicateKeyError):
            await card2.insert()

    async def test_create_card_missing_name(self, data):
        card_data = data.card
        card_data["version"] = card_data.get("version", "1.0.0")
        card_data["created_at"] = datetime.now()
        bad_data = card_data.copy()
        del bad_data["name"]
        with pytest.raises(ValueError):
            card = Card(**bad_data)
            await card.insert()


@pytest.mark.skip("standard")
@pytest.mark.usefixtures("init_db", "cleanup_db")
@pytest.mark.asyncio
class TestCardModelRead:
    async def test_read_existing_card(self, data):
        card_data = data.card
        card = Card(**card_data)
        await card.insert()
        found = await Card.get(card.id)
        assert found is not None
        assert found.name == card_data["name"]
        assert found.text == card_data["text"]
        assert found.version is not None

    async def test_read_nonexistent_card(self):
        fake_id = PydanticObjectId()
        found = await Card.get(fake_id)
        assert found is None

    async def test_read_all_cards(self, data):
        cards = []
        for _ in range(3):
            card_data = data.card
            card_data["name"] = card_data["name"] + str(_)
            card = Card(**card_data)
            await card.insert()
            cards.append(card)
        all_cards = await Card.find_all().to_list()
        assert len(all_cards) >= 3
        names = [c.name for c in all_cards]
        for card in cards:
            assert card.name in names


@pytest.mark.skip("standard")
@pytest.mark.usefixtures("init_db", "cleanup_db")
@pytest.mark.asyncio
class TestCardModelUpdate:
    async def test_update_card_name(self, data):
        card_data = data.card
        card = Card(**card_data)
        await card.insert()
        card.name = "new_card_name"
        await card.save()
        updated = await Card.get(card.id)
        assert updated is not None
        assert updated.name == "new_card_name"

    async def test_update_card_text(self, data):
        card_data = data.card
        card = Card(**card_data)
        await card.insert()
        card.text = "Updated card text"
        await card.save()
        updated = await Card.get(card.id)
        assert updated is not None
        assert updated.text == "Updated card text"


@pytest.mark.skip("standard")
@pytest.mark.usefixtures("init_db", "cleanup_db")
@pytest.mark.asyncio
class TestCardModelDelete:
    async def test_delete_card(self, data):
        card_data = data.card
        card = Card(**card_data)
        await card.insert()
        await card.delete()
        deleted = await Card.get(card.id)
        assert deleted is None


@pytest.mark.skip("standard")
@pytest.mark.usefixtures("init_db", "cleanup_db")
@pytest.mark.asyncio
class TestCardLinkFunctionality:
    async def test_cardlink_creation_with_nested_game(self, data):
        card_data = data.card
        game_data = data.game
        game = Game(**game_data)
        await game.insert()
        game_link = GameLink.from_instance(game)
        card_data["game"] = game_link
        card = Card(**card_data)
        await card.insert()
        card_link = card.to_link()
        assert isinstance(card_link, CardLink)
        assert card_link.name == card.name
        assert card_link.version == card.version
        assert card_link.id == card.id
        assert hasattr(card_link, "link")
        assert isinstance(card_link.link, Link)
        # Check nested game link
        assert isinstance(card_link.game, GameLink)
        assert card_link.game.name == game.name
        assert card_link.game.version == game.version
        assert card_link.game.id == game.id

    async def test_cardlink_to_list_item_with_nested_game(self, data):
        card_data = data.card
        game_data = data.game
        game = Game(**game_data)
        await game.insert()
        game_link = GameLink.from_instance(game)
        card_data["game"] = game_link
        card = Card(**card_data)
        await card.insert()
        card_link = CardLink.from_instance(card)
        assert isinstance(card_link.game, GameLink)
        list_item = card_link.to_list_item()
        assert isinstance(list_item, CardListItem)
        assert list_item.name == card.name
        assert list_item.version == card.version
        assert list_item.id == card.id
        # Check nested game list item
        assert isinstance(list_item.game, GameListItem)
        assert list_item.game.name == game.name
        assert list_item.game.version == game.version
        assert list_item.game.id == game.id

    async def test_cardlink_missing_fields_raises(self, data):
        game_data = data.game
        game = Game(**game_data)
        await game.insert()
        game_link = game.to_link()
        
        data_dict = {
            "id": PydanticObjectId(),
            "name": "sample",
            "version": "1.0.0",
            "link": Link,
            "game": game_link,
        }
        for key in data_dict:
            data_copy = data_dict.copy()
            del data_copy[key]
            with pytest.raises(ValidationError):
                CardLink(**data_copy)
