import pytest
from beanie import PydanticObjectId, Link
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from pydantic import ValidationError

from fast_backend.app.models import Deck, DeckLink, User, UserLink, Game, GameLink
from fast_backend.app.schemas import DeckListItem, UserListItem, GameListItem

@pytest.mark.skip("standard")
@pytest.mark.usefixtures("init_db", "cleanup_db")
@pytest.mark.asyncio
class TestDeckModelCreate:
    async def test_create_deck_success(self, data, managers):
        user_data = data.hashed_user
        game_data = data.game
        deck_data = data.deck

        owner = User(**user_data)
        await owner.insert()
        game = Game(**game_data)
        await game.insert()

        deck_data["owner"] = owner.to_link()
        deck_data["game"] = game.to_link()
        deck_data["is_public"] = True
        deck = Deck(**deck_data)
        await deck.insert()
        assert isinstance(deck.id, PydanticObjectId)
        assert deck.name == deck_data["name"]
        assert deck.owner.id == owner.id
        assert deck.game.id == game.id
        assert deck.is_public is True
        assert deck.created_at is not None
        assert isinstance(deck.created_at, datetime)
        assert deck.version is not None

        db_deck = await Deck.get(deck.id)
        assert db_deck is not None
        assert db_deck.name == deck.name
        assert db_deck.owner.id == owner.id
        assert db_deck.game.id == game.id
        assert db_deck.is_public == deck.is_public
        assert db_deck.created_at is not None
        assert db_deck.description == deck_data["description"]
        assert db_deck.version is not None

    async def test_create_deck_duplicate_name_fails(self, data):
        user_data = data.hashed_user
        game_data = data.game
        deck_data = data.deck

        owner = User(**user_data)
        await owner.insert()
        game = Game(**game_data)
        await game.insert()

        deck_data["owner"] = owner.to_link()
        deck_data["game"] = game.to_link()
        deck_data["is_public"] = True
        deck1 = Deck(**deck_data)
        await deck1.insert()
        deck2_data = deck_data.copy()
        deck2 = Deck(**deck2_data)
        with pytest.raises(DuplicateKeyError) as e:
            await deck2.insert()
        assert "dup key" in str(e.value).lower()
        assert "name" in str(e.value).lower()
        assert "version" in str(e.value).lower()

    async def test_create_deck_missing_name(self, data):
        user_data = data.hashed_user
        game_data = data.game
        deck_data = data.deck

        owner = User(**user_data)
        await owner.insert()
        game = Game(**game_data)
        await game.insert()

        deck_data["owner"] = owner.to_link()
        deck_data["game"] = game.to_link()
        deck_data["is_public"] = True
        deck_data["description"] = deck_data.get("description", "Test deck description")
        deck_data["version"] = deck_data.get("version", "1.0.0")
        del deck_data["name"]
        with pytest.raises(ValueError) as e:
            deck = Deck(**deck_data)
            await deck.insert()
        assert "field required" in str(e.value).lower()
        assert "name" in str(e.value).lower()

@pytest.mark.skip("standard")
@pytest.mark.usefixtures("init_db", "cleanup_db")
@pytest.mark.asyncio
class TestDeckModelRead:
    async def test_read_existing_deck(self, data):
        user_data = data.hashed_user
        game_data = data.game
        deck_data = data.deck

        owner = User(**user_data)
        await owner.insert()
        game = Game(**game_data)
        await game.insert()

        deck_data["owner"] = owner.to_link()
        deck_data["game"] = game.to_link()
        deck_data["is_public"] = True
        deck = Deck(**deck_data)
        await deck.insert()
        found = await Deck.get(deck.id)
        assert found is not None
        assert found.name == deck_data["name"]
        assert found.owner.id == owner.id
        assert found.game.id == game.id
        assert found.is_public is True
        assert found.description == deck_data["description"]
        assert found.version is not None
        assert found.created_at is not None
        assert isinstance(found.created_at, datetime)

    async def test_read_nonexistent_deck(self):
        fake_id = PydanticObjectId()
        found = await Deck.get(fake_id)
        assert found is None

    async def test_read_all_decks(self, data):
        user_data = data.hashed_user
        owner = User(**user_data)
        await owner.insert()
        owner_link = owner.to_link()
        game_data = data.game
        game = Game(**game_data)
        await game.insert()
        game_link = game.to_link()
            
        decks = []
        for _ in range(3):
            deck_data = data.deck
            deck_data["owner"] = owner_link
            deck_data["game"] = game_link
            deck_data["is_public"] = True
            deck = Deck(**deck_data)
            await deck.insert()
            decks.append(deck)
        all_decks = await Deck.find_all().to_list()
        assert len(all_decks) >= 3
        names = [d["name"] for d in data.decks]
        descriptions = [d["description"] for d in data.decks]
        for deck in decks:
            assert deck.name in names
            assert deck.owner.id == owner.id
            assert deck.game.id == game.id
            assert deck.is_public is True
            assert deck.description in descriptions
            assert deck.version is not None
            assert deck.created_at is not None
            assert isinstance(deck.created_at, datetime)

@pytest.mark.skip("standard")
@pytest.mark.usefixtures("init_db", "cleanup_db")
@pytest.mark.asyncio
class TestDeckModelUpdate:
    async def test_update_deck_name(self, data):
        user_data = data.hashed_user
        game_data = data.game
        deck_data = data.deck

        owner = User(**user_data)
        await owner.insert()
        game = Game(**game_data)
        await game.insert()

        deck_data["owner"] = owner.to_link()
        deck_data["game"] = game.to_link()
        deck_data["is_public"] = True
        deck = Deck(**deck_data)
        await deck.insert()
        deck.name = "new_deck_name"
        await deck.save()
        updated = await Deck.get(deck.id)
        assert updated is not None
        assert updated.name == "new_deck_name"
        assert updated.owner.id == owner.id
        assert updated.game.id == game.id
        assert updated.is_public == deck.is_public
        assert updated.description == deck.description
        assert updated.version == deck.version
        assert updated.created_at == deck.created_at

    async def test_update_deck_is_public(self, data):
        user_data = data.hashed_user
        game_data = data.game
        deck_data = data.deck

        owner = User(**user_data)
        await owner.insert()
        game = Game(**game_data)
        await game.insert()

        deck_data["owner"] = owner.to_link()
        deck_data["game"] = game.to_link()
        deck_data["is_public"] = False
        deck = Deck(**deck_data)
        await deck.insert()
        assert not deck.is_public
        deck.is_public = True
        await deck.save()
        updated = await Deck.get(deck.id)
        assert updated is not None
        assert updated.is_public is True

@pytest.mark.skip("standard")
@pytest.mark.usefixtures("init_db", "cleanup_db")
@pytest.mark.asyncio
class TestDeckModelDelete:
    async def test_delete_deck(self, data):
        user_data = data.hashed_user
        game_data = data.game
        deck_data = data.deck

        owner = User(**user_data)
        await owner.insert()
        game = Game(**game_data)
        await game.insert()

        deck_data["owner"] = owner.to_link()
        deck_data["game"] = game.to_link()
        deck_data["is_public"] = True
        deck = Deck(**deck_data)
        await deck.insert()
        await deck.delete()
        deleted = await Deck.get(deck.id)
        assert deleted is None

@pytest.mark.skip("standard")
@pytest.mark.usefixtures("init_db", "cleanup_db")
@pytest.mark.asyncio
class TestDeckLinkFunctionality:
    async def test_decklink_creation_with_nested_links(self, data):
        user_data = data.hashed_user
        game_data = data.game
        deck_data = data.deck

        owner = User(**user_data)
        await owner.insert()
        game = Game(**game_data)
        await game.insert()

        deck_data["owner"] = owner.to_link()
        deck_data["game"] = game.to_link()
        deck_data["is_public"] = True
        deck = Deck(**deck_data)
        await deck.insert()
        deck_link = deck.to_link()
        assert isinstance(deck_link, DeckLink)
        assert deck_link.name == deck.name
        assert deck_link.version == deck.version
        assert deck_link.id == deck.id
        assert hasattr(deck_link, "link")
        assert isinstance(deck_link.link, Link)
        assert deck_link.is_public == deck.is_public
        # Check nested owner link
        assert isinstance(deck_link.owner, UserLink)
        assert isinstance(deck_link.owner.link, Link)
        assert deck_link.owner.username == owner.username
        assert deck_link.owner.id == owner.id
        # Check nested game link
        assert isinstance(deck_link.game, GameLink)
        assert isinstance(deck_link.game.link, Link)
        assert deck_link.game.name == game.name
        assert deck_link.game.version == game.version
        assert deck_link.game.id == game.id
        

    async def test_decklink_to_list_item_with_nested_links(self, data):
        user_data = data.hashed_user
        game_data = data.game
        deck_data = data.deck

        owner = User(**user_data)
        await owner.insert()
        game = Game(**game_data)
        await game.insert()

        deck_data["owner"] = owner.to_link()
        deck_data["game"] = game.to_link()
        deck_data["is_public"] = True
        deck = Deck(**deck_data)
        await deck.insert()
        deck_link = deck.to_link()
        list_item = deck_link.to_list_item()
        assert isinstance(list_item, DeckListItem)
        assert list_item.name == deck.name
        assert list_item.id == deck.id
        assert list_item.is_public == deck.is_public
        # Check nested owner list item
        assert isinstance(list_item.owner, UserListItem)
        assert list_item.owner.username == owner.username
        assert list_item.owner.id == owner.id
        # Check nested game list item
        assert isinstance(list_item.game, GameListItem)
        assert list_item.game.name == game.name
        assert list_item.game.version == game.version
        assert list_item.game.id == game.id

    async def test_decklink_missing_fields_raises(self, data):
        user_data = data.hashed_user
        game_data = data.game
        owner = User(**user_data)
        await owner.insert()
        game = Game(**game_data)
        await game.insert()
        owner_link = owner.to_link()
        game_link = game.to_link()
        data_dict = {
            "id": PydanticObjectId(),
            "name": "sample",
            "version": "1.0.0",
            "link": Link,
            "owner": owner_link,
            "game": game_link,
            "is_public": True,
        }
        for key in data_dict:
            data_copy = data_dict.copy()
            del data_copy[key]
            with pytest.raises(ValidationError):
                DeckLink(**data_copy)