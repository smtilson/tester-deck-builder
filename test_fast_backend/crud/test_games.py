import pytest
import random
from beanie.odm.fields import PydanticObjectId

from fast_backend.app.core.exceptions import NotFoundException
from fast_backend.app.crud.games import GameManager
from fast_backend.app.models.games import Game
from fast_backend.app.schemas.games import GameCreate, GameUpdate


@pytest.mark.skip("standard")
@pytest.mark.asyncio
@pytest.mark.usefixtures("init_db")
class TestGameManagerCreate:
    """Integration tests for GameManager create operations."""

    async def test_create_game_success(self, all_test_data):
        game_data = all_test_data.game
        game_create = GameCreate(**game_data)

        result = await GameManager.create_game(game_create)

        assert result.name == game_data["name"]
        assert result.version == game_data["version"]
        assert isinstance(result.id, PydanticObjectId)
        assert result.created_at is not None
        assert result.updated_at is None

        db_game = await Game.get(result.id)
        assert db_game.name == game_data["name"]
        assert db_game.version == game_data["version"]

    async def test_create_game_minimal_data(self):
        game_create = GameCreate(name="Minimal Game")

        result = await GameManager.create_game(game_create)

        assert result.name == "Minimal Game"
        assert result.version == "0.0.0"
        assert isinstance(result.id, PydanticObjectId)

    async def test_create_multiple_games_different_names(self):
        game1 = GameCreate(name="First Game", version="1.0.0")
        game2 = GameCreate(name="Second Game", version="2.0.0")

        result1 = await GameManager.create_game(game1)
        result2 = await GameManager.create_game(game2)

        assert result1.id != result2.id
        assert result1.name == "First Game"
        assert result2.name == "Second Game"


@pytest.mark.skip("standard")
@pytest.mark.asyncio
@pytest.mark.usefixtures("init_db")
class TestGameManagerRead:
    """Integration tests for GameManager read operations."""

    async def test_get_game_by_id_success(self, setup_games):
        created_game = random.choice(setup_games)

        result = await GameManager.get_game(created_game.id)

        assert result is not None
        assert result.id == created_game.id
        assert result.name == created_game.name
        assert result.version == created_game.version

    async def test_get_game_by_id_not_found(self, setup_games):
        random_id = PydanticObjectId()
        with pytest.raises(NotFoundException) as e:
            await GameManager.get_game(random_id)
        assert str(random_id) in str(e.value)

    async def test_get_all_games_returns_all(self, setup_games):
        result = await GameManager.get_all_games()

        assert len(result) == len(setup_games)
        game_names = [game.name for game in result]
        expected_names = [game.name for game in setup_games]
        assert set(game_names) == set(expected_names)

    async def test_get_all_games_empty_database(self):
        await Game.all().delete()
        result = await GameManager.get_all_games()
        assert result == []


@pytest.mark.skip("standard")
@pytest.mark.asyncio
@pytest.mark.usefixtures("init_db")
class TestGameManagerUpdate:
    """Integration tests for GameManager update operations."""

    async def test_update_game_success(self, single_game):
        update_data = GameUpdate(
            name=single_game.name + " updated",
            version="9.9.9",
        )

        result = await GameManager.update_game(single_game.id, update_data)

        assert result is not None
        assert result.id == single_game.id
        assert result.name == single_game.name + " updated"
        assert result.version == "9.9.9"
        assert result.updated_at is not None

        db_game = await Game.get(single_game.id)
        assert db_game.name == single_game.name + " updated"
        assert db_game.version == "9.9.9"

    async def test_update_game_partial_update_name_only(self, single_game):
        update_data = GameUpdate(name="Only Name Changed")

        result = await GameManager.update_game(single_game.id, update_data)

        assert result is not None
        assert result.name == "Only Name Changed"
        assert result.version == single_game.version
        assert result.id == single_game.id

    async def test_update_game_partial_update_version_only(self, single_game):
        update_data = GameUpdate(version="Only Version Changed")

        result = await GameManager.update_game(single_game.id, update_data)

        assert result is not None
        assert result.version == "Only Version Changed"
        assert result.name == single_game.name
        assert result.id == single_game.id

    async def test_update_game_empty_update(self, single_game):
        update_data = GameUpdate()

        result = await GameManager.update_game(single_game.id, update_data)

        assert result is not None
        assert result.name == single_game.name
        assert result.version == single_game.version
        assert result.id == single_game.id

    async def test_update_game_not_found(self):
        random_id = PydanticObjectId()
        update_data = GameUpdate(name="New Name")

        with pytest.raises(NotFoundException) as e:
            await GameManager.update_game(random_id, update_data)
        assert str(random_id) in str(e.value)


@pytest.mark.skip("standard")
@pytest.mark.asyncio
@pytest.mark.usefixtures("init_db")
class TestGameManagerDelete:
    """Integration tests for GameManager delete operations."""

    async def test_delete_game_success(self):
        game = await GameManager.create_game(
            GameCreate(name="Test Game", version="1.0.0")
        )
        id = game.id
        result = await GameManager.delete_game(id)
        assert result is True

        with pytest.raises(NotFoundException) as e:
            await GameManager.get_game(id)
        assert str(id) in str(e.value)

        game = await Game.get(id)
        assert game is None

    async def test_delete_game_not_found(self):
        random_id = PydanticObjectId()
        with pytest.raises(NotFoundException) as e:
            await GameManager.delete_game(random_id)
        assert str(random_id) in str(e.value)

    async def test_delete_game_multiple_times(self, single_game):
        id = single_game.id
        result1 = await GameManager.delete_game(id)
        assert result1 is True

        with pytest.raises(NotFoundException) as e:
            await GameManager.delete_game(id)
        assert str(id) in str(e.value)