import pytest
import random
from beanie.odm.fields import PydanticObjectId
from pymongo.errors import DuplicateKeyError
from datetime import datetime

from fast_backend.app.exceptions import NotFoundException
from fast_backend.app.models import Deck
from fast_backend.app.schemas import DeckCreate, DeckUpdate, DeckResponse

@pytest.mark.skip("standard")
@pytest.mark.usefixtures("init_db", "cleanup_db")
@pytest.mark.asyncio
class TestDeckManagerCreate:
    """Integration tests for DeckManager create operations."""

    async def test_create_deck_success(self, managers, data, setup):
        """Test successful deck creation with valid data."""
        deck_data = data.deck
        deck_data["name"] += " - the new version"
        owner = await setup.user
        game = await setup.game
        deck_data["owner_id"] = owner.id
        deck_data["game_id"] = game.id
        deck_create = DeckCreate(**deck_data)

        result = await managers.deck.create(deck_create)

        # Check all relevant fields in DeckResponse
        assert isinstance(result.id, PydanticObjectId)
        assert result.name == deck_data["name"]
        assert result.description == deck_data.get("description", None)
        assert result.is_public == deck_data.get("is_public", False)
        assert result.version == "1.0.0"
        assert isinstance(result.created_at, datetime)
        assert result.updated_at is None
        assert result.owner.id == owner.id
        assert result.game.id == game.id

        # Verify deck exists in database and check all fields
        db_deck = await Deck.get(result.id)
        assert db_deck is not None
        await db_deck.fetch_link(Deck.owner)
        await db_deck.fetch_link(Deck.game)
        assert db_deck.name == deck_data["name"]
        assert db_deck.description == deck_data.get("description", None)
        assert db_deck.is_public == deck_data.get("is_public", False)
        assert db_deck.version == "1.0.0"
        assert db_deck.owner.id == owner.id
        assert db_deck.game.id == game.id
        assert isinstance(db_deck.created_at, datetime)
        assert db_deck.updated_at is None
        assert db_deck.cards == []

    async def test_create_deck_minimal_data(self, managers, setup):
        """Test creating deck with minimal required data."""
        owner = await setup.user
        game = await setup.game
        deck_create = DeckCreate(
            name="Minimal Deck", 
            owner_id=owner.id,
            game_id=game.id
        )

        result = await managers.deck.create(deck_create)

        assert result.name == "Minimal Deck"
        assert result.description is None
        assert result.is_public is False  # Default value
        assert result.version == "1.0.0"
        assert result.owner.id == owner.id
        assert result.game.id == game.id
        assert isinstance(result.created_at, datetime)
        assert result.updated_at is None
        
        # Check in database
        db_deck = await Deck.get(result.id)
        assert db_deck is not None
        await db_deck.fetch_link(Deck.owner)
        await db_deck.fetch_link(Deck.game)
        assert db_deck.name == "Minimal Deck"
        assert db_deck.description is None
        assert db_deck.is_public is False
        assert db_deck.version == "1.0.0"
        assert db_deck.owner.id == owner.id
        assert db_deck.game.id == game.id
        assert isinstance(db_deck.created_at, datetime)
        assert db_deck.updated_at is None
        assert db_deck.cards == []

    async def test_create_deck_duplicate_name_fails(self, managers, setup, data):
        """Test that creating deck with duplicate name fails."""
        owner = await setup.user
        game = await setup.game
        deck1_data = data.deck
        deck2_data = data.deck
        assert deck1_data["name"] != deck2_data["name"]
        deck1_data["owner_id"] = owner.id
        deck1_data["game_id"] = game.id
        deck2_data["owner_id"] = owner.id
        deck2_data["game_id"] = game.id
        deck2_data["name"] = deck1_data["name"]  # Force duplicate name
        deck1_create = DeckCreate(**deck1_data)
        deck2_create = DeckCreate(**deck2_data)
        # Create first deck
        deck1 = await managers.deck.create(deck1_create)

        # Attempt to create second deck with same name should fail
        with pytest.raises(DuplicateKeyError):
            await managers.deck.create(deck2_create)
        
@pytest.mark.skip("standard")
@pytest.mark.asyncio
@pytest.mark.usefixtures("init_db", "cleanup_db")
class TestDeckManagerRead:
    """Integration tests for DeckManager read operations."""

    async def test_get_deck_by_id_success(self, managers, setup):
        decks = await setup.decks()
        single_deck = random.choice(decks)
        deck_id = single_deck.id

        result = await managers.deck.get(deck_id)

        assert result is not None
        assert isinstance(result.id, PydanticObjectId)
        assert result.id == deck_id
        assert result.name == single_deck.name
        assert result.description == single_deck.description
        assert result.is_public == single_deck.is_public
        assert result.version == single_deck.version
        assert result.owner.id == single_deck.owner.id
        assert result.game.id == single_deck.game.id
        _ = {"second": 0, "microsecond": 0}
        assert result.created_at.replace(**_) == single_deck.created_at.replace(**_)
        if result.updated_at is None:
            assert single_deck.updated_at is None
        else:
            assert result.updated_at.replace(**_) == single_deck.updated_at.replace(**_)

    async def test_get_deck_by_id_not_found(self, managers):
        non_existent_id = PydanticObjectId()
        with pytest.raises(NotFoundException) as e:
            await managers.deck.get(non_existent_id)
        assert str(non_existent_id) in str(e.value)

    async def test_get_all_decks_returns_all(self, managers, setup):
        decks = await setup.decks()
        result = await managers.deck.get_all()

        assert len(result) == len(decks)
        deck_names = [deck.name for deck in result]
        expected_names = [deck.name for deck in decks]
        assert set(deck_names) == set(expected_names)
        
        # Check all fields for each deck
        for deck in result:
            matching_deck = next(d for d in decks if d.id == deck.id)
            assert deck.name == matching_deck.name
            assert deck.description == matching_deck.description
            assert deck.is_public == matching_deck.is_public
            assert deck.version == matching_deck.version
            assert deck.owner is not None
            assert deck.owner.id == matching_deck.owner.id
            assert deck.game is not None
            assert deck.game.id == matching_deck.game.id
            assert isinstance(deck.created_at, datetime)
            assert deck.updated_at == matching_deck.updated_at

    async def test_get_all_decks_empty_database(self, managers):
        await managers.deck.delete_all()
        with pytest.raises(NotFoundException) as e:
            await managers.deck.get_all()
        assert "No records" in str(e.value)

@pytest.mark.skip("standard")
@pytest.mark.asyncio
@pytest.mark.usefixtures("init_db", "cleanup_db")
class TestDeckManagerUpdate:
    """Integration tests for DeckManager update operations."""

    async def test_update_deck_success(self, managers, setup):
        decks = await setup.decks()
        single_deck = random.choice(decks)
        update_data = DeckUpdate(
            name=single_deck.name + " Updated",
            is_public=not single_deck.is_public,
            version="2.0.0"
        )

        result = await managers.deck.update(single_deck.id, update_data)

        assert result is not None
        assert result.id == single_deck.id
        assert result.name == single_deck.name + " Updated"
        assert result.is_public is not single_deck.is_public
        assert result.version == "2.0.0"
        assert result.updated_at is not None
        
        # Other fields should remain unchanged
        assert result.description == single_deck.description
        assert result.owner.id == single_deck.owner.id
        assert result.game.id == single_deck.game.id
        
        # Verify update persisted in database
        db_deck = await Deck.get(single_deck.id)
        assert db_deck is not None
        await db_deck.fetch_link(Deck.owner)
        await db_deck.fetch_link(Deck.game)
        assert db_deck.name == single_deck.name + " Updated"
        assert db_deck.is_public is not single_deck.is_public
        assert db_deck.version == "2.0.0"
        assert db_deck.description == single_deck.description
        assert db_deck.owner.id == single_deck.owner.id
        assert db_deck.game.id == single_deck.game.id
        assert db_deck.updated_at is not None

    async def test_update_deck_partial_name_only(self, managers, setup):
        decks = await setup.decks()
        single_deck = random.choice(decks)
        update_data = DeckUpdate(name="Only Name Changed")

        result = await managers.deck.update(single_deck.id, update_data)

        assert result is not None
        assert result.name == "Only Name Changed"
        # Other fields should remain unchanged
        assert result.description == single_deck.description
        assert result.is_public == single_deck.is_public
        assert result.version == single_deck.version
        assert result.owner.id == single_deck.owner.id
        assert result.game.id == single_deck.game.id

    async def test_update_deck_is_public_only(self, managers, setup):
        decks = await setup.decks()
        single_deck = random.choice(decks)
        update_data = DeckUpdate(is_public=not single_deck.is_public)

        result = await managers.deck.update(single_deck.id, update_data)

        assert result is not None
        assert result.is_public is not single_deck.is_public
        # Other fields should remain unchanged
        assert result.name == single_deck.name
        assert result.description == single_deck.description
        assert result.version == single_deck.version
        assert result.owner.id == single_deck.owner.id
        assert result.game.id == single_deck.game.id

    async def test_update_deck_empty_update(self, managers, setup):
        decks = await setup.decks()
        single_deck = random.choice(decks)
        update_data = DeckUpdate()

        result = await managers.deck.update(single_deck.id, update_data)

        assert result is not None
        # All fields should remain unchanged
        assert result.name == single_deck.name
        assert result.description == single_deck.description
        assert result.is_public == single_deck.is_public
        assert result.version == single_deck.version
        assert result.owner.id == single_deck.owner.id
        assert result.game.id == single_deck.game.id

    async def test_update_deck_not_found(self, managers):
        non_existent_id = PydanticObjectId()
        update_data = DeckUpdate(name="New Name")

        with pytest.raises(NotFoundException) as e:
            await managers.deck.update(non_existent_id, update_data)
        assert str(non_existent_id) in str(e.value)

@pytest.mark.skip("standard")
@pytest.mark.asyncio
@pytest.mark.usefixtures("init_db", "cleanup_db")
class TestDeckManagerDelete:
    """Integration tests for DeckManager delete operations."""

    async def test_delete_deck_success(self, managers, setup):
        decks = await setup.decks()
        single_deck = random.choice(decks)
        deck_id = single_deck.id
        
        # Ensure deck exists before deletion
        deck = await Deck.get(deck_id)
        assert deck is not None
        
        result = await managers.deck.delete(deck_id)
        assert result is True

        # Verify deck is actually deleted
        with pytest.raises(NotFoundException) as e:
            await managers.deck.get(deck_id)
        assert str(deck_id) in str(e.value)
        
        # Verify it's gone from the database
        deleted_deck = await Deck.get(deck_id)
        assert deleted_deck is None

    async def test_delete_deck_not_found(self, managers):
        non_existent_id = PydanticObjectId()

        with pytest.raises(NotFoundException) as e:
            await managers.deck.delete(non_existent_id)
        assert str(non_existent_id) in str(e.value)

    async def test_delete_deck_multiple_times(self, managers, setup):
        decks = await setup.decks()
        single_deck = random.choice(decks)
        deck_id = single_deck.id
        result1 = await managers.deck.delete(deck_id)
        assert result1 is True

        with pytest.raises(NotFoundException) as e:
            await managers.deck.delete(deck_id)
        assert str(deck_id) in str(e.value)


@pytest.mark.skip("special")
@pytest.mark.asyncio
@pytest.mark.usefixtures("init_db", "cleanup_db")
class TestDeckManagerEdgeCases:
    """Integration tests for DeckManager edge cases and error conditions."""

    async def test_create_deck_with_very_long_name(self, managers, setup):
        long_name = "A" * 255  # Maximum length according to model
        owner = await setup.user
        game = await setup.game
        deck_create = DeckCreate(
            name=long_name, 
            owner_id=owner.id,
            game_id=game.id
        )

        result = await managers.deck.create(deck_create)

        assert result.name == long_name
        assert len(result.name) == 255
        assert result.owner.id == owner.id
        assert result.game.id == game.id

    async def test_create_deck_with_very_long_description(self, managers, setup):
        long_description = "This is a very long description. " * 100
        owner = await setup.user
        game = await setup.game
        deck_create = DeckCreate(
            name="Long Description Deck",
            description=long_description,
            owner_id=owner.id,
            game_id=game.id
        )

        result = await managers.deck.create(deck_create)

        assert result.description == long_description
        assert result.name == "Long Description Deck"
        assert result.owner.id == owner.id
        assert result.game.id == game.id

    async def test_create_deck_with_empty_description_string(self, managers, setup):
        owner = await setup.user
        game = await setup.game
        deck_create = DeckCreate(
            name="Empty Description Deck", 
            description="", 
            owner_id=owner.id,
            game_id=game.id
        )

        result = await managers.deck.create(deck_create)

        assert result.description == ""
        assert result.name == "Empty Description Deck"
        assert result.owner.id == owner.id
        assert result.game.id == game.id

    async def test_deck_id_uniqueness(self, managers, setup):
        owner = await setup.user
        game = await setup.game
        deck1 = await managers.deck.create(
            DeckCreate(name="Deck 1", owner_id=owner.id, game_id=game.id)
        )
        deck2 = await managers.deck.create(
            DeckCreate(name="Deck 2", owner_id=owner.id, game_id=game.id)
        )
        deck3 = await managers.deck.create(
            DeckCreate(name="Deck 3", owner_id=owner.id, game_id=game.id)
        )

        # IDs should be different
        assert deck1.id != deck2.id != deck3.id
        
        # Check they exist in database with correct IDs
        assert await Deck.get(deck1.id) is not None
        assert await Deck.get(deck2.id) is not None
        assert await Deck.get(deck3.id) is not None

    async def test_update_deck_duplicate_name_constraint(self, managers, setup):
        owner = await setup.user
        game = await setup.game
        deck1 = await managers.deck.create(
            DeckCreate(name="First Deck", owner_id=owner.id, game_id=game.id)
        )
        deck2 = await managers.deck.create(
            DeckCreate(name="Second Deck", owner_id=owner.id, game_id=game.id)
        )

        # Try to update deck2 to have same name as deck1
        update_data = DeckUpdate(name="First Deck")

        with pytest.raises(Exception):  # Replace with specific exception when implemented
            await managers.deck.update(deck2.id, update_data)
