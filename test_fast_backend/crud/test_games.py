import pytest
import random
from beanie.odm.fields import PydanticObjectId
from datetime import datetime

from fast_backend.app.core.exceptions import NotFoundException
from fast_backend.app.models import Game
from fast_backend.app.schemas import GameCreate, GameUpdate, GameResponse, GameListItem, UserListItem


@pytest.mark.skip("standard")
@pytest.mark.asyncio
@pytest.mark.usefixtures("init_db", "cleanup_db")
class TestGameManagerCreate:
    """Integration tests for GameManager create operations."""

    async def test_create_game_success(self, game_manager, user_manager, all_test_data, setup_users):
        game_data = all_test_data.game
        num1 = random.randint(2,len(setup_users))
        num2 = random.randint(2,len(setup_users))
        designer_ids = list({user.id for user in random.sample(setup_users, num1)})
        developer_ids = list({user.id for user in random.sample(setup_users, num2)})
        game_data["designer_ids"] = designer_ids
        game_data["developer_ids"] = developer_ids
        game_create = GameCreate(**game_data)
        result = await game_manager.create(game_create)

        # Check all relevant fields in GameResponse
        assert isinstance(result.id, PydanticObjectId)
        assert result.name == game_data["name"]
        assert result.version == game_data.get("version", "0.0.0")
        assert result.description == game_data["description"]
        assert result.publisher == game_data["publisher"]
        assert result.release_date == game_data["release_date"]
        assert isinstance(result.created_at, datetime)
        assert result.updated_at is None

        # Designers and developers should be lists of UserListItem
        designers = [await user_manager.get_list_item(user_id) for user_id in designer_ids]
        assert isinstance(result.designers, list)
        for u in result.designers:
            if u in designers:
                designers.remove(u)
        assert len(designers) == 0
        
        developers = [await user_manager.get_list_item(user_id) for user_id in developer_ids]
        assert isinstance(result.developers, list)
        for u in result.developers:
            if u in developers:
                developers.remove(u)
        assert len(developers) == 0

        # Check values in database
        db_game = await Game.get(result.id)
        assert db_game is not None
        assert db_game.name == game_data["name"]
        assert db_game.version == game_data["version"]
        assert db_game.description == game_data["description"]
        assert db_game.publisher == game_data["publisher"]
        assert db_game.release_date == game_data["release_date"]
        # Designers and developers are Link[User], check ids
        assert {u.id for u in db_game.designers} == set(designer_ids)
        assert len(db_game.designers) == len(designer_ids)
        assert {u.id for u in db_game.developers} == set(developer_ids)
        assert len(db_game.developers) == len(developer_ids)
    async def test_create_game_minimal_data(self, game_manager):
        game_create = GameCreate(name="Minimal Game")
        result = await game_manager.create(game_create)
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

    async def test_create_multiple_games_different_names(self, game_manager, all_test_data):
        game1_data = all_test_data.game
        game2_data = all_test_data.game
        assert game1_data != game2_data, "Test data for two games should be different"
        game1 = GameCreate(**game1_data)
        game2 = GameCreate(**game2_data)
        result1 = await game_manager.create(game1)
        result2 = await game_manager.create(game2)
        assert result1.id != result2.id
        assert result1.name == game1_data["name"]
        assert result2.name == game2_data["name"]
        assert result1.version == game1_data["version"]
        assert result2.version == game2_data["version"] 


@pytest.mark.skip("standard")
@pytest.mark.asyncio
@pytest.mark.usefixtures("init_db", "cleanup_db")
class TestGameManagerRead:
    """Integration tests for GameManager read operations."""

    #need to to test the get model method of the manager
    
    async def test_get_game_by_id_success(self, game_manager, setup_games):
        created_game = random.choice(setup_games)
        result = await game_manager.get(created_game.id)
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
        # Designers and developers
        assert isinstance(result.designers, list)
        assert isinstance(result.developers, list)
        assert all(isinstance(designer, UserListItem) for designer in result.designers)
        assert all(isinstance(developer, UserListItem) for developer in result.developers)
        assert [u.id for u in result.designers] == [u.id for u in created_game.designers]
        assert [u.id for u in result.developers] == [u.id for u in created_game.developers]

    async def test_get_game_by_id_not_found(self, game_manager):
        random_id = PydanticObjectId()
        with pytest.raises(NotFoundException) as e:
            await game_manager.get(random_id)
        assert str(random_id) in str(e.value)

    async def test_get_all_games_returns_all(self, game_manager, setup_games):
        result = await game_manager.get_all()
        assert len(result) == len(setup_games)
        game_names = [game.name for game in result]
        expected_names = [game.name for game in setup_games]
        assert set(game_names) == set(expected_names)
        
        # Check all fields for each game
        for game in result:
            # Find the matching expected game
            expected = next((g for g in setup_games if g.id == game.id), None)
            assert expected is not None
            
            assert game.name == expected.name
            assert game.version == expected.version
            assert game.description == expected.description
            assert game.publisher == expected.publisher
            assert game.release_date == expected.release_date
            assert isinstance(game.created_at, datetime)
            assert game.updated_at == expected.updated_at
            
            # Designers and developers
            assert isinstance(game.designers, list)
            assert isinstance(game.developers, list)
            assert all(isinstance(designer, UserListItem) for designer in game.designers)
            assert all(isinstance(developer, UserListItem) for developer in game.developers)
            assert [u.id for u in game.designers] == [u.id for u in expected.designers]
            assert [u.id for u in game.developers] == [u.id for u in expected.developers]

    async def test_get_all_games_empty_database(self, game_manager):
        await Game.all().delete()
        result = await game_manager.get_all()
        assert result == []
    
    async def test_game_response_has_correct_user_list_items(self, game_manager, setup_games, user_manager):
        """Test that designers and developers are correctly returned as UserListItems."""
        # Get a random game from setup_games
        created_game = random.choice(setup_games)
        
        # Fetch it using the manager
        result = await game_manager.get(created_game.id)
        
        # Check that designers and developers are lists of UserListItem
        assert isinstance(result.designers, list)
        assert isinstance(result.developers, list)
        assert all(isinstance(designer, UserListItem) for designer in result.designers)
        assert all(isinstance(developer, UserListItem) for developer in result.developers)
        
        # Check each designer's details
        for designer in result.designers:
            # Verify it's a UserListItem with the expected structure
            assert isinstance(designer.id, PydanticObjectId)
            assert isinstance(designer.username, str)
            assert isinstance(designer.email, str)
            
            # Verify it matches what we'd get from the user_manager
            user_list_item = await user_manager.get_list_item(designer.id)
            assert designer == user_list_item
            
            # Check it doesn't have sensitive fields
            assert not hasattr(designer, "password")
            assert not hasattr(designer, "hashed_password")
        
        # Check each developer's details
        for developer in result.developers:
            assert isinstance(developer.id, PydanticObjectId)
            assert isinstance(developer.username, str)
            assert isinstance(developer.email, str)
            
            # Verify it matches what we'd get from the user_manager
            user_list_item = await user_manager.get_list_item(developer.id)
            assert developer == user_list_item
            
            # Check it doesn't have sensitive fields
            assert not hasattr(developer, "password")
            assert not hasattr(developer, "hashed_password")


@pytest.mark.skip("standard")
@pytest.mark.asyncio
@pytest.mark.usefixtures("init_db", "cleanup_db")
class TestGameManagerUpdate:
    """Integration tests for GameManager update operations."""

    async def test_update_game_success(self, game_manager, single_game):
        update_data = GameUpdate(
            name=single_game.name + " updated",
            version="9.9.9",
            description="Updated description",
            publisher="Updated publisher",
            release_date=datetime(2025, 8, 26, 12, 0, 0)
        )
        result = await game_manager.update(single_game.id, update_data)
        assert result is not None
        assert result.id == single_game.id
        assert result.name == single_game.name + " updated"
        assert result.version == "9.9.9"
        assert result.description == "Updated description"
        assert result.publisher == "Updated publisher"
        assert result.release_date == datetime(2025, 8, 26, 12, 0, 0)
        assert result.updated_at is not None
        # Designers and developers should remain unchanged
        assert [u.id for u in result.designers] == [u.id for u in single_game.designers]
        assert [u.id for u in result.developers] == [u.id for u in single_game.developers]
        # Check values in database
        db_game = await Game.get(single_game.id)
        assert db_game is not None
        assert db_game.name == single_game.name + " updated"
        assert db_game.version == "9.9.9"
        assert db_game.description == "Updated description"
        assert db_game.publisher == "Updated publisher"
        assert db_game.release_date == datetime(2025, 8, 26, 12, 0, 0)

    async def test_update_game_partial_update_name_only(self, game_manager, single_game):
        update_data = GameUpdate(name="Only Name Changed")
        result = await game_manager.update(single_game.id, update_data)
        assert result is not None
        assert result.name == "Only Name Changed"
        assert result.version == single_game.version
        assert result.id == single_game.id

    async def test_update_game_partial_update_version_only(self, game_manager, single_game):
        update_data = GameUpdate(version="Only Version Changed")
        result = await game_manager.update(single_game.id, update_data)
        assert result is not None
        assert result.version == "Only Version Changed"
        assert result.name == single_game.name
        assert result.id == single_game.id

    async def test_update_game_empty_update(self, game_manager, single_game):
        update_data = GameUpdate()
        result = await game_manager.update(single_game.id, update_data)
        assert result is not None
        assert result.name == single_game.name
        assert result.version == single_game.version
        assert result.id == single_game.id

    async def test_update_game_not_found(self, game_manager):
        random_id = PydanticObjectId()
        update_data = GameUpdate(name="New Name")
        with pytest.raises(NotFoundException) as e:
            await game_manager.update(random_id, update_data)
        assert str(random_id) in str(e.value)


@pytest.mark.skip("standard")
@pytest.mark.asyncio
@pytest.mark.usefixtures("init_db", "cleanup_db")
class TestGameManagerDelete:
    """Integration tests for GameManager delete operations."""

    async def test_delete_game_success(self, game_manager):
        game = await game_manager.create(
            GameCreate(name="Test Game", version="1.0.0")
        )
        id = game.id
        result = await game_manager.delete(id)
        assert result is True

        with pytest.raises(NotFoundException) as e:
            await game_manager.get(id)
        assert str(id) in str(e.value)

        game = await Game.get(id)
        assert game is None

    async def test_delete_game_not_found(self, game_manager):
        random_id = PydanticObjectId()
        with pytest.raises(NotFoundException) as e:
            await game_manager.delete(random_id)
        assert str(random_id) in str(e.value)

    async def test_delete_game_multiple_times(self, game_manager, single_game):
        id = single_game.id
        result1 = await game_manager.delete(id)
        assert result1 is True

        with pytest.raises(NotFoundException) as e:
            await game_manager.delete(id)
        assert str(id) in str(e.value)