import pytest
from beanie import PydanticObjectId, Link
from datetime import datetime, timedelta
from pydantic import ValidationError
from pymongo.errors import DuplicateKeyError

from fast_backend.app.models import Game, GameLink, User, UserLink
from fast_backend.app.schemas import GameListItem, UserListItem

@pytest.mark.skip("standard")
@pytest.mark.usefixtures("init_db", "cleanup_db")
@pytest.mark.asyncio
class TestGameModelCreate:
    async def test_create_game_success(self, data):
        game_data = data.game
        game_data["release_date"] = datetime.now()
        game = Game(**game_data)
        await game.insert()
        assert isinstance(game.id, PydanticObjectId)
        assert game.name == game_data["name"]
        assert game.version == game_data.get("version", "0.0.0")
        assert game.description == game_data.get("description")
        assert game.publisher == game_data.get("publisher")
        assert isinstance(game.release_date, datetime)
        assert isinstance(game.designers, list)
        assert isinstance(game.developers, list)

        db_game = await Game.get(game.id)
        assert db_game is not None
        assert db_game.name == game.name
        assert db_game.version == game.version
        assert db_game.description == game.description
        assert db_game.publisher == game.publisher
        assert db_game.designers == game.designers
        assert db_game.developers == game.developers

        delta = abs(db_game.release_date - game.release_date)
        assert delta < timedelta(milliseconds=2)

    async def test_create_game_duplicate_name_version_fails(self, data):
        game_data = data.game
        game1 = Game(**game_data)
        await game1.insert()
        game2_data = game_data.copy()
        game2_data["description"] = "Another game"
        game2 = Game(**game2_data)
        with pytest.raises(DuplicateKeyError) as e:
            await game2.insert()
        assert "dup key" in str(e.value).lower()
        assert "name" in str(e.value).lower()
        assert "version" in str(e.value).lower()

    async def test_create_game_missing_name(self, data):
        game_data = data.game
        del game_data["name"]
        with pytest.raises(ValueError):
            game = Game(**game_data)
            await game.insert()

@pytest.mark.skip("standard")
@pytest.mark.usefixtures("init_db", "cleanup_db")
@pytest.mark.asyncio
class TestGameModelRead:
    async def test_read_existing_game(self, data):
        game_data = data.game
        game = Game(**game_data)
        await game.insert()
        found = await Game.get(game.id)
        assert found is not None
        assert found.name == game_data["name"]
        assert found.version == game_data.get("version", "0.0.0")
        assert found.description == game_data.get("description")
        assert found.publisher == game_data.get("publisher")
        assert found.release_date == game_data.get("release_date")
        assert found.designers == game_data.get("designers", [])
        assert found.developers == game_data.get("developers", [])

    async def test_read_all_games(self, data):
        games = []
        for _ in range(3):
            game_data = data.game.copy()
            game_data["name"] = game_data["name"] + str(_)
            game = Game(**game_data)
            await game.insert()
            games.append(game)
        all_games = await Game.find_all().to_list()
        assert len(all_games) >= 3
        names = [g.name for g in all_games]
        for game in games:
            assert game.name in names

    async def test_read_nonexistent_game(self):
        fake_id = PydanticObjectId()
        found = await Game.get(fake_id)
        assert found is None

@pytest.mark.skip("standard")
@pytest.mark.usefixtures("init_db", "cleanup_db")
@pytest.mark.asyncio
class TestGameModelUpdate:
    async def test_update_game_name(self, data):
        game_data = data.game
        game = Game(**game_data)
        await game.insert()
        game.name = "new_game_name"
        await game.save()
        updated = await Game.get(game.id)
        assert updated is not None
        assert updated.name == "new_game_name"

    async def test_update_game_version(self, data):
        game_data = data.game
        game = Game(**game_data)
        await game.insert()
        game.version = "1.2.3"
        await game.save()
        updated = await Game.get(game.id)
        assert updated is not None
        assert updated.version == "1.2.3"

@pytest.mark.skip("standard")
@pytest.mark.usefixtures("init_db", "cleanup_db")
@pytest.mark.asyncio
class TestGameModelDelete:
    async def test_delete_game(self, data):
        game_data = data.game
        game = Game(**game_data)
        await game.insert()
        await game.delete()
        deleted = await Game.get(game.id)
        assert deleted is None

#@pytest.mark.skip("standard")
@pytest.mark.usefixtures("init_db", "cleanup_db")
@pytest.mark.asyncio
class TestGameLinkFunctionality:
    async def test_gamelink_creation(self, data):
        game_data = data.game
        game = Game(**game_data)
        await game.insert()
        game_link = game.to_link()
        assert isinstance(game_link, GameLink)
        assert game_link.name == game.name
        assert game_link.version == game.version
        assert game_link.id == game.id
        assert hasattr(game_link, "link")
        assert isinstance(game_link.link, Link)

    async def test_gamelink_to_list_item(self, data):
        game_data = data.game
        game = Game(**game_data)
        await game.insert()
        game_link = game.to_link()
        list_item = game_link.to_list_item()
        assert isinstance(list_item, GameListItem)
        assert list_item.name == game.name
        assert list_item.version == game.version
        assert list_item.id == game.id

    async def test_gamelink_missing_fields_raises(self):
        data = {
            "id": PydanticObjectId(),
            "name": "sample",
            "version": "0.0.0",
            "link": Link,
        }
        for key in data:
            data_copy = data.copy()
            del data_copy[key]
            with pytest.raises(ValidationError):
                GameLink(**data_copy)
