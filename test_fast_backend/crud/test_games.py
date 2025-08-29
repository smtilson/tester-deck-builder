import pytest
import random
from beanie.odm.fields import PydanticObjectId
from datetime import datetime

from fast_backend.app.core.exceptions import NotFoundException
from fast_backend.app.models import Game
from fast_backend.app.schemas import GameCreate, GameUpdate, GameResponse, GameListItem, UserListItem


#@pytest.mark.skip("standard")
@pytest.mark.asyncio
@pytest.mark.usefixtures("init_db", "cleanup_db")
class TestGameManagerCreate:
    """Integration tests for GameManager create operations."""

    async def test_create_game_success(self, managers, data, setup):
        users = await setup.users()
        game_data = data.game
        num1 = random.randint(2, len(users))
        num2 = random.randint(2, len(users))
        designer_ids = list({user.id for user in random.sample(users, num1)})
        developer_ids = list({user.id for user in random.sample(users, num2)})
        game_data["designer_ids"] = designer_ids
        game_data["developer_ids"] = developer_ids
        game_create = GameCreate(**game_data)
        result = await managers.game.create(game_create)

        # Check all relevant fields in GameResponse
        assert isinstance(result.id, PydanticObjectId)
        assert result.name == game_data["name"]
        assert result.version == game_data.get("version", "0.0.0")
        assert result.description == game_data["description"]
        assert result.publisher == game_data["publisher"]
        assert result.release_date == game_data["release_date"]
        assert isinstance(result.created_at, datetime)
        assert result.updated_at is None

        designers = [user for user in users if user.id in designer_ids]
        developers = [user for user in users if user.id in developer_ids]
        assert isinstance(result.designers, list)
        assert set(u.id for u in result.designers) == set(u.id for u in designers)
        assert isinstance(result.developers, list)
        assert set(u.id for u in result.developers) == set(u.id for u in developers)

        db_game = await Game.get(result.id)
        assert db_game is not None
        assert db_game.name == game_data["name"]
        assert db_game.version == game_data["version"]
        assert db_game.description == game_data["description"]
        assert db_game.publisher == game_data["publisher"]
        assert db_game.release_date == game_data["release_date"]
        assert {u.id for u in db_game.designers} == set(designer_ids)
        assert {u.id for u in db_game.developers} == set(developer_ids)

    async def test_create_game_minimal_data(self, managers):
        game_create = GameCreate(name="Minimal Game")
        result = await managers.game.create(game_create)
        assert result.name == "Minimal Game"
        assert result.version == "0.0.0"
        assert isinstance(result.id, PydanticObjectId)
        assert result.description is None
        assert result.publisher is None
        assert result.release_date is None
        assert isinstance(result.created_at, datetime)
        assert result.updated_at is None
        assert result.designers == []
        assert result.developers == []

    async def test_create_multiple_games_different_names(self, setup):
        games = await setup.games()
        assert len(games) >= 2
        game1, game2 = games[:2]
        assert game1.id != game2.id
        assert game1.name != game2.name
        assert game1.version == game1.version
        assert game2.version == game2.version

#@pytest.mark.skip("standard")
@pytest.mark.asyncio
@pytest.mark.usefixtures("init_db", "cleanup_db")
class TestGameManagerRead:
    """Integration tests for GameManager read operations."""

    async def test_get_game_by_id_success(self, setup, managers):
        games = await setup.games()
        created_game = random.choice(games)
        result = await managers.game.get(created_game.id)
        assert result is not None
        assert isinstance(result.id, PydanticObjectId)
        assert result.id == created_game.id
        assert result.name == created_game.name
        assert result.version == created_game.version
        assert result.description == created_game.description
        assert result.publisher == created_game.publisher
        assert result.release_date == created_game.release_date
        assert isinstance(result.created_at, datetime)
        assert result.updated_at == created_game.updated_at
        assert isinstance(result.designers, list)
        assert isinstance(result.developers, list)
        assert [u.id for u in result.designers] == [u.id for u in created_game.designers]
        assert [u.id for u in result.developers] == [u.id for u in created_game.developers]

    async def test_get_game_by_id_not_found(self, managers):
        random_id = PydanticObjectId()
        with pytest.raises(NotFoundException) as e:
            await managers.game.get(random_id)
        assert str(random_id) in str(e.value)

    async def test_get_all_games_returns_all(self, setup, managers):
        games = await setup.games()
        result = await managers.game.get_all()
        assert len(result) == len(games)
        game_names = [game.name for game in result]
        expected_names = [game.name for game in games]
        assert set(game_names) == set(expected_names)
        for game in result:
            expected = next((g for g in games if g.id == game.id), None)
            assert expected is not None
            assert game.name == expected.name
            assert game.version == expected.version
            assert game.description == expected.description
            assert game.publisher == expected.publisher
            assert game.release_date == expected.release_date
            assert isinstance(game.created_at, datetime)
            assert game.updated_at == expected.updated_at
            assert isinstance(game.designers, list)
            assert isinstance(game.developers, list)
            assert [u.id for u in game.designers] == [u.id for u in expected.designers]
            assert [u.id for u in game.developers] == [u.id for u in expected.developers]

    async def test_get_all_games_empty_database(self, managers):
        await managers.game.delete_all()
        with pytest.raises(NotFoundException) as e:
            await managers.game.get_all()
        assert "No records" in str(e.value)
        assert "Game" in str(e.value)

    async def test_game_response_has_correct_user_list_items(self, setup, managers):
        games = await setup.games()
        created_game = random.choice(games)
        result = await managers.game.get(created_game.id)
        assert isinstance(result.designers, list)
        assert isinstance(result.developers, list)
        assert all(isinstance(designer, UserListItem) for designer in result.designers)
        assert all(isinstance(developer, UserListItem) for developer in result.developers)
        for designer in result.designers:
            assert isinstance(designer.id, PydanticObjectId)
            assert isinstance(designer.username, str)
            assert isinstance(designer.email, str)
            # You may want to check for absence of password fields here
            assert not hasattr(designer, "password")
            assert not hasattr(designer, "hashed_password")
        for developer in result.developers:
            assert isinstance(developer.id, PydanticObjectId)
            assert isinstance(developer.username, str)
            assert isinstance(developer.email, str)
            assert not hasattr(developer, "password")
            assert not hasattr(developer, "hashed_password")

#@pytest.mark.skip("standard")
@pytest.mark.asyncio
@pytest.mark.usefixtures("init_db", "cleanup_db")
class TestGameManagerUpdate:
    """Integration tests for GameManager update operations."""

    async def test_update_game_success(self, setup, managers):
        games = await setup.games()
        single_game = random.choice(games)
        update_data = GameUpdate(
            name=single_game.name + " updated",
            version="9.9.9",
            description="Updated description",
            publisher="Updated publisher",
            release_date=datetime(2025, 8, 26, 12, 0, 0)
        )
        result = await managers.game.update(single_game.id, update_data)
        assert result is not None
        assert result.id == single_game.id
        assert result.name == single_game.name + " updated"
        assert result.version == "9.9.9"
        assert result.description == "Updated description"
        assert result.publisher == "Updated publisher"
        assert result.release_date == datetime(2025, 8, 26, 12, 0, 0)
        assert result.updated_at is not None
        assert [u.id for u in result.designers] == [u.id for u in single_game.designers]
        assert [u.id for u in result.developers] == [u.id for u in single_game.developers]
        db_game = await Game.get(single_game.id)
        assert db_game is not None
        assert db_game.name == single_game.name + " updated"
        assert db_game.version == "9.9.9"
        assert db_game.description == "Updated description"
        assert db_game.publisher == "Updated publisher"
        assert db_game.release_date == datetime(2025, 8, 26, 12, 0, 0)

    async def test_update_game_partial_update_name_only(self, setup, managers):
        games = await setup.games()
        single_game = random.choice(games)
        update_data = GameUpdate(name="Only Name Changed")
        result = await managers.game.update(single_game.id, update_data)
        assert result is not None
        assert result.name == "Only Name Changed"
        assert result.version == single_game.version
        assert result.id == single_game.id

    async def test_update_game_partial_update_version_only(self, setup, managers):
        games = await setup.games()
        single_game = random.choice(games)
        update_data = GameUpdate(version="Only Version Changed")
        result = await managers.game.update(single_game.id, update_data)
        assert result is not None
        assert result.version == "Only Version Changed"
        assert result.name == single_game.name
        assert result.id == single_game.id

    async def test_update_game_empty_update(self, setup, managers):
        games = await setup.games()
        single_game = random.choice(games)
        update_data = GameUpdate()
        result = await managers.game.update(single_game.id, update_data)
        assert result is not None
        assert result.name == single_game.name
        assert result.version == single_game.version
        assert result.id == single_game.id

    async def test_update_game_not_found(self, managers):
        random_id = PydanticObjectId()
        update_data = GameUpdate(name="New Name")
        with pytest.raises(NotFoundException) as e:
            await managers.game.update(random_id, update_data)
        assert str(random_id) in str(e.value)

#@pytest.mark.skip("standard")
@pytest.mark.asyncio
@pytest.mark.usefixtures("init_db", "cleanup_db")
class TestGameManagerDelete:
    """Integration tests for GameManager delete operations."""

    async def test_delete_game_success(self, managers):
        game_create = GameCreate(name="Test Game", version="1.0.0")
        game = await managers.game.create(game_create)
        id = game.id
        result = await managers.game.delete(id)
        assert result is True

        with pytest.raises(NotFoundException) as e:
            await managers.game.get(id)
        assert str(id) in str(e.value)

        game = await Game.get(id)
        assert game is None

    async def test_delete_game_not_found(self, managers):
        random_id = PydanticObjectId()
        with pytest.raises(NotFoundException) as e:
            await managers.game.delete(random_id)
        assert str(random_id) in str(e.value)

    async def test_delete_game_multiple_times(self, setup, managers):
        games = await setup.games()
        single_game = random.choice(games)
        id = single_game.id
        result1 = await managers.game.delete(id)
        assert result1 is True

        with pytest.raises(NotFoundException) as e:
            await managers.game.delete(id)
        assert str(id) in str(e.value)