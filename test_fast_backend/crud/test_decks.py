import pytest

import random

from fast_backend.app.crud.decks import DeckManager
from fast_backend.app.models.decks import Deck
from fast_backend.app.crud.users import UserManager
from fast_backend.app.schemas.decks import DeckCreate, DeckUpdate
from fast_backend.app.schemas.users import UserCreate


@pytest.mark.skip("standard")
@pytest.mark.usefixtures("init_db")
@pytest.mark.asyncio
class TestDeckManagerCreate:
    """Integration tests for DeckManager create operations."""

    async def test_create_deck_success(self, deck_test_data, single_user):
        """Test successful deck creation with valid data."""
        deck_data = random.choice(deck_test_data)
        deck_create = DeckCreate(
            **deck_data,
            owner=single_user,
        )

        result = await DeckManager.create_deck_record(deck_create)

        assert result.name == deck_data["name"]
        assert result.description == deck_data["description"]
        assert result.is_valid == deck_data["is_valid"]
        assert isinstance(result.id, int)
        assert result.created_at is not None
        assert result.updated_at is not None
        assert result.owner.id == single_user.id

        # Verify deck exists in database
        db_deck = await Deck.get(id=result.id)
        assert db_deck.name == deck_data["name"]
        assert db_deck.description == deck_data["description"]
        assert db_deck.is_valid == deck_data["is_valid"]
        assert db_deck.owner_id == single_user.id

    async def test_create_deck_minimal_data(self, single_user):
        """Test creating deck with minimal required data."""
        deck_create = DeckCreate(name="Minimal Deck", owner=single_user)

        result = await DeckManager.create_deck_record(deck_create)

        assert result.name == "Minimal Deck"
        assert result.description is None
        assert result.is_valid is False  # Default value
        assert result.owner.id == single_user.id

    async def test_create_deck_duplicate_name_fails(self, init_db, single_user):
        """Test that creating deck with duplicate name fails."""
        deck_create = DeckCreate(name="Unique Deck Name", owner=single_user)

        # Create first deck
        await DeckManager.create_deck_record(deck_create)

        # Attempt to create second deck with same name should fail
        with pytest.raises(IntegrityError):
            await DeckManager.create_deck_record(deck_create)


@pytest.mark.skip("standard")
@pytest.mark.asyncio
class TestDeckManagerRead:
    """Integration tests for DeckManager read operations."""

    async def test_get_deck_by_id_success(self, setup_decks):
        """Test successful retrieval of deck by ID."""
        created_deck = random.choice(setup_decks)

        result = await DeckManager.get_deck(created_deck.id)

        assert result is not None
        assert result.id == created_deck.id
        assert result.name == created_deck.name
        assert result.description == created_deck.description
        assert result.is_valid == created_deck.is_valid
        assert result.owner.id == created_deck.owner.id

    async def test_get_deck_by_id_not_found(self, init_db):
        """Test that getting non-existent deck returns None."""
        non_existent_id = 99999

        result = await DeckManager.get_deck(non_existent_id)

        assert result is None

    async def test_get_all_decks_returns_all(self, setup_decks, deck_test_data):
        """Test that get_all_decks returns all created decks."""
        result = await DeckManager.get_all_decks()

        assert len(result) == len(deck_test_data)
        deck_names = [deck.name for deck in result]
        expected_names = [deck["name"] for deck in deck_test_data]
        assert set(deck_names) == set(expected_names)

    async def test_get_all_decks_empty_database(self, init_db):
        """Test get_all_decks with empty database."""
        # Clear all decks
        await Deck.all().delete()

        result = await DeckManager.get_all_decks()

        assert result == []


@pytest.mark.skip("standard")
@pytest.mark.asyncio
class TestDeckManagerUpdate:
    """Integration tests for DeckManager update operations."""

    async def test_update_deck_success(self, user_test_data, single_deck):
        """Test successful deck update."""
        owner, deck = single_deck["owner"], single_deck["test_deck"]
        all_other_user_data = [
            user_data
            for user_data in user_test_data
            if user_data["username"] != owner.username
        ]
        new_user_data = random.choice(all_other_user_data)
        new_owner = await UserManager.create_user(UserCreate(**new_user_data))
        update_data = DeckUpdate(
            name=deck.name + " Updated",
            description=deck.description + " Updated",
            is_valid=True,
            owner=new_owner,
        )

        result = await DeckManager.update_deck(single_deck["test_deck"].id, update_data)

        assert result is not None
        assert result.id == single_deck["test_deck"].id
        assert result.name == deck.name + " Updated"
        assert result.description == deck.description + " Updated"
        assert result.is_valid is True
        # Owner should be updated to the new owner
        assert result.owner.id == new_owner.id

        # Verify update persisted in database
        db_deck = await Deck.get(id=single_deck["test_deck"].id)
        assert db_deck.name == deck.name + " Updated"
        assert db_deck.description == deck.description + " Updated"
        assert db_deck.is_valid is True
        assert db_deck.owner_id == new_owner.id

    async def test_update_deck_partial_name_only(self, single_deck):
        """Test partial deck update with only name field."""
        update_data = DeckUpdate(name="Only Name Changed")

        result = await DeckManager.update_deck(single_deck["test_deck"].id, update_data)

        assert result is not None
        assert result.name == "Only Name Changed"
        # Other fields should remain unchanged
        assert result.description == single_deck["test_deck"].description
        assert result.is_valid == single_deck["test_deck"].is_valid
        assert result.owner.id == single_deck["owner"].id

    async def test_update_deck_partial_description_only(self, single_deck):
        """Test partial deck update with only description field."""
        update_data = DeckUpdate(description="Only description changed")

        result = await DeckManager.update_deck(single_deck["test_deck"].id, update_data)

        assert result is not None
        assert result.description == "Only description changed"
        # Other fields should remain unchanged
        assert result.name == single_deck["test_deck"].name
        assert result.is_valid == single_deck["test_deck"].is_valid
        assert result.owner.id == single_deck["owner"].id

    async def test_update_deck_set_description_to_null(self, single_deck):
        """Test updating deck description to null."""
        update_data = DeckUpdate(description=None)

        result = await DeckManager.update_deck(single_deck["test_deck"].id, update_data)

        assert result is not None
        assert result.description is None
        assert result.name == single_deck["test_deck"].name

    async def test_update_deck_toggle_validity(self, single_deck):
        """Test updating deck validity status."""
        new_validity = not single_deck["test_deck"].is_valid
        update_data = DeckUpdate(is_valid=new_validity)

        result = await DeckManager.update_deck(single_deck["test_deck"].id, update_data)

        assert result is not None
        assert result.is_valid == new_validity
        assert result.name == single_deck["test_deck"].name

    async def test_update_deck_empty_update(self, single_deck):
        """Test update with no fields provided."""
        update_data = DeckUpdate()

        result = await DeckManager.update_deck(single_deck["test_deck"].id, update_data)

        assert result is not None
        # All fields should remain unchanged
        assert result.name == single_deck["test_deck"].name
        assert result.description == single_deck["test_deck"].description
        assert result.is_valid == single_deck["test_deck"].is_valid

    async def test_update_deck_not_found(self, init_db):
        """Test updating non-existent deck returns None."""
        non_existent_id = 99999
        update_data = DeckUpdate(name="New Name")

        result = await DeckManager.update_deck(non_existent_id, update_data)

        assert result is None


@pytest.mark.skip("standard")
@pytest.mark.asyncio
@pytest.mark.usefixtures("init_db")
class TestDeckManagerDelete:
    """Integration tests for DeckManager delete operations."""

    async def test_delete_deck_success(self, single_deck):
        """Test successful deck deletion."""
        deck = single_deck["test_deck"]
        deck_id = deck.id
        deck_db = Deck.get(id=deck_id)
        assert deck_db is not None

        result = await DeckManager.delete_deck(deck_id)

        assert result is True

        # Verify deck is actually deleted
        deleted_deck = await DeckManager.get_deck(deck_id)
        assert deleted_deck is None
        with pytest.raises(DoesNotExist):
            deleted_deck_db = await Deck.get(id=deck_id)

    async def test_delete_deck_not_found(self):
        """Test deleting non-existent deck returns False."""
        non_existent_id = 99999

        result = await DeckManager.delete_deck(non_existent_id)

        assert result is False

    async def test_delete_deck_multiple_times(self, single_deck):
        """Test deleting same deck multiple times."""
        # First deletion should succeed
        result1 = await DeckManager.delete_deck(single_deck["test_deck"].id)
        assert result1 is True

        # Second deletion should fail
        result2 = await DeckManager.delete_deck(single_deck["test_deck"].id)
        assert result2 is False


@pytest.mark.skip("special")
@pytest.mark.asyncio
class TestDeckManagerEdgeCases:
    """Integration tests for DeckManager edge cases and error conditions."""

    async def test_create_deck_with_very_long_name(self, init_db, single_user):
        """Test creating deck with maximum length name."""
        long_name = "A" * 255  # Maximum length according to model
        deck_create = DeckCreate(name=long_name, owner=single_user)

        result = await DeckManager.create_deck_record(deck_create)

        assert result.name == long_name
        assert len(result.name) == 255

    async def test_create_deck_with_very_long_description(self, init_db, single_user):
        """Test creating deck with very long description."""
        long_description = "This is a very long description. " * 100
        deck_create = DeckCreate(
            name="Long Description Deck",
            description=long_description,
            owner=single_user,
        )

        result = await DeckManager.create_deck_record(deck_create)

        assert result.description == long_description
        assert result.name == "Long Description Deck"

    async def test_create_deck_with_empty_description_string(
        self, init_db, single_user
    ):
        """Test creating deck with empty string as description."""
        deck_create = DeckCreate(
            name="Empty Description Deck", description="", owner=single_user
        )

        result = await DeckManager.create_deck_record(deck_create)

        assert result.description == ""
        assert result.name == "Empty Description Deck"

    async def test_deck_id_autoincrement(self, init_db, single_user):
        """Test that deck IDs are properly auto-incremented."""
        deck1 = await DeckManager.create_deck_record(
            DeckCreate(name="Deck 1", owner=single_user)
        )
        deck2 = await DeckManager.create_deck_record(
            DeckCreate(name="Deck 2", owner=single_user)
        )
        deck3 = await DeckManager.create_deck_record(
            DeckCreate(name="Deck 3", owner=single_user)
        )

        # IDs should be different and in ascending order
        assert deck1.id != deck2.id != deck3.id
        assert deck1.id < deck2.id < deck3.id

    async def test_update_deck_duplicate_name_constraint(self, init_db, single_user):
        """Test that updating deck to duplicate name fails."""
        # Create two decks
        deck1 = await DeckManager.create_deck_record(
            DeckCreate(name="First Deck", owner=single_user)
        )
        deck2 = await DeckManager.create_deck_record(
            DeckCreate(name="Second Deck", owner=single_user)
        )

        # Try to update deck2 to have same name as deck1
        update_data = DeckUpdate(name="First Deck")

        with pytest.raises(IntegrityError):
            await DeckManager.update_deck(deck2.id, update_data)

    async def test_deck_owner_relationship_constraint(self, init_db, single_user):
        """Test that deck requires valid owner relationship."""
        # Create deck with valid owner
        deck_create = DeckCreate(name="Test Deck", owner=single_user)
        deck = await DeckManager.create_deck_record(deck_create)

        # Verify owner relationship exists
        assert deck.owner_id == single_user.id

        # Verify deck can be retrieved with owner relationship
        retrieved_deck = await DeckManager.get_deck(deck.id)
        assert retrieved_deck.owner_id == single_user.id
