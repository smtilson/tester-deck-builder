import pytest
import pytest_asyncio
import uuid
import random
from tortoise.exceptions import IntegrityError, DoesNotExist

from fast_backend.app.crud.decks import DeckRepo
from fast_backend.app.models.decks import Deck
from fast_backend.app.crud.users import UserRepo
from fast_backend.app.schemas.decks import DeckCreate, DeckUpdate
from fast_backend.app.schemas.users import UserCreate, UserResponse


@pytest_asyncio.fixture
async def setup_owner(init_db, user_test_data):
    """Create a test user to own decks."""
    user_data = random.choice(user_test_data)
    user_create = UserCreate(**user_data)
    owner = await UserRepo.create_user(user_create)
    return owner


@pytest_asyncio.fixture
async def setup_decks(init_db, user_test_data, deck_test_data):
    """Create test decks for read operations."""
    # Create owners first
    user1_data = user_test_data[0]
    user2_data = user_test_data[1]
    owner1 = await UserRepo.create_user(UserCreate(**user1_data))
    owner2 = await UserRepo.create_user(UserCreate(**user2_data))

    # Create decks
    created_decks = []
    for deck_data in deck_test_data:
        deck_data_copy = deck_data.copy()
        deck_data_copy["owner"] = (
            owner1 if deck_data_copy["owner_id"] == user1_data["id"] else owner2
        )
        deck_create = DeckCreate(**deck_data_copy)
        created_deck = await DeckRepo.create_deck_record(deck_create)
        created_decks.append(created_deck)
    return created_decks


@pytest_asyncio.fixture
async def setup_deck(init_db, deck_test_data, setup_owner):
    """Create a test deck for update operations."""
    deck_data = random.choice(deck_test_data)
    deck_create = DeckCreate(
        name=deck_data["name"],
        description=deck_data["description"],
        is_valid=deck_data["is_valid"],
        owner=setup_owner,
    )
    test_deck = await DeckRepo.create_deck_record(deck_create)
    return {"owner": setup_owner, "test_deck": test_deck}


@pytest.mark.asyncio
@pytest.mark.asyncio
class TestDeckRepoCreate:
    """Integration tests for DeckRepo create operations."""

    async def test_create_deck_success(self, init_db, deck_test_data, setup_owner):
        """Test successful deck creation with valid data."""
        deck_data = random.choice(deck_test_data)
        deck_create = DeckCreate(
            name=deck_data["name"],
            description=deck_data["description"],
            is_valid=deck_data["is_valid"],
            owner=setup_owner,
        )

        result = await DeckRepo.create_deck_record(deck_create)

        assert result.name == deck_data["name"]
        assert result.description == deck_data["description"]
        assert result.is_valid == deck_data["is_valid"]
        assert isinstance(result.id, int)
        assert result.created_at is not None
        assert result.updated_at is not None
        assert result.owner_id == setup_owner.id

        # Verify deck exists in database
        db_deck = await Deck.get(id=result.id)
        assert db_deck.name == deck_data["name"]
        assert db_deck.description == deck_data["description"]
        assert db_deck.is_valid == deck_data["is_valid"]
        assert db_deck.owner_id == setup_owner.id

    async def test_create_deck_minimal_data(self, init_db, setup_owner):
        """Test creating deck with minimal required data."""
        deck_create = DeckCreate(name="Minimal Deck", owner=setup_owner)

        result = await DeckRepo.create_deck_record(deck_create)

        assert result.name == "Minimal Deck"
        assert result.description is None
        assert result.is_valid is False  # Default value
        assert result.owner_id == setup_owner.id

    async def test_create_deck_duplicate_name_fails(self, init_db, setup_owner):
        """Test that creating deck with duplicate name fails."""
        deck_create = DeckCreate(name="Unique Deck Name", owner=setup_owner)

        # Create first deck
        await DeckRepo.create_deck_record(deck_create)

        # Attempt to create second deck with same name should fail
        with pytest.raises(IntegrityError):
            await DeckRepo.create_deck_record(deck_create)


@pytest.mark.asyncio
@pytest.mark.asyncio
class TestDeckRepoRead:
    """Integration tests for DeckRepo read operations."""

    async def test_get_deck_by_id_success(self, setup_decks):
        """Test successful retrieval of deck by ID."""
        created_deck = random.choice(setup_decks)

        result = await DeckRepo.get_deck(created_deck.id)

        assert result is not None
        assert result.id == created_deck.id
        assert result.name == created_deck.name
        assert result.description == created_deck.description
        assert result.is_valid == created_deck.is_valid
        assert result.owner_id == created_deck.owner_id

    async def test_get_deck_by_id_not_found(self, init_db):
        """Test that getting non-existent deck returns None."""
        non_existent_id = 99999

        result = await DeckRepo.get_deck(non_existent_id)

        assert result is None

    async def test_get_all_decks_returns_all(self, setup_decks, deck_test_data):
        """Test that get_all_decks returns all created decks."""
        result = await DeckRepo.get_all_decks()

        assert len(result) == len(deck_test_data)
        deck_names = [deck.name for deck in result]
        expected_names = [deck["name"] for deck in deck_test_data]
        assert set(deck_names) == set(expected_names)

    async def test_get_all_decks_empty_database(self, init_db):
        """Test get_all_decks with empty database."""
        # Clear all decks
        await Deck.all().delete()

        result = await DeckRepo.get_all_decks()

        assert result == []


@pytest.mark.asyncio
@pytest.mark.asyncio
class TestDeckRepoUpdate:
    """Integration tests for DeckRepo update operations."""

    async def test_update_deck_success(self, user_test_data, setup_deck):
        """Test successful deck update."""
        owner, deck = setup_deck["owner"], setup_deck["test_deck"]
        all_other_user_data = [
            user_data
            for user_data in user_test_data
            if user_data["id"] != owner.id
        ]
        new_user_data = random.choice(all_other_user_data)
        new_owner = await UserRepo.create_user(UserCreate(**new_user_data))
        update_data = DeckUpdate(
            name=deck.name + " Updated",
            description=deck.description + " Updated",
            is_valid=True,
            owner=new_owner,
        )

        result = await DeckRepo.update_deck(setup_deck["test_deck"].id, update_data)

        assert result is not None
        assert result.id == setup_deck["test_deck"].id
        assert result.name == deck.name + " Updated"
        assert result.description == deck.description + " Updated"
        assert result.is_valid is True
        # Owner should be updated to the new owner
        assert result.owner_id == new_owner.id

        # Verify update persisted in database
        db_deck = await Deck.get(id=setup_deck["test_deck"].id)
        assert db_deck.name == deck.name + " Updated"
        assert db_deck.description == deck.description + " Updated"
        assert db_deck.is_valid is True
        assert db_deck.owner_id == new_owner.id

    async def test_update_deck_partial_name_only(self, setup_deck):
        """Test partial deck update with only name field."""
        update_data = DeckUpdate(name="Only Name Changed")

        result = await DeckRepo.update_deck(setup_deck["test_deck"].id, update_data)

        assert result is not None
        assert result.name == "Only Name Changed"
        # Other fields should remain unchanged
        assert result.description == setup_deck["test_deck"].description
        assert result.is_valid == setup_deck["test_deck"].is_valid
        assert result.owner_id == setup_deck["owner"].id

    async def test_update_deck_partial_description_only(self, setup_deck):
        """Test partial deck update with only description field."""
        update_data = DeckUpdate(description="Only description changed")

        result = await DeckRepo.update_deck(setup_deck["test_deck"].id, update_data)

        assert result is not None
        assert result.description == "Only description changed"
        # Other fields should remain unchanged
        assert result.name == setup_deck["test_deck"].name
        assert result.is_valid == setup_deck["test_deck"].is_valid
        assert result.owner_id == setup_deck["owner"].id

    async def test_update_deck_set_description_to_null(self, setup_deck):
        """Test updating deck description to null."""
        update_data = DeckUpdate(description=None)

        result = await DeckRepo.update_deck(setup_deck["test_deck"].id, update_data)

        assert result is not None
        assert result.description is None
        assert result.name == setup_deck["test_deck"].name

    async def test_update_deck_toggle_validity(self, setup_deck):
        """Test updating deck validity status."""
        original_validity = setup_deck["test_deck"].is_valid
        update_data = DeckUpdate(is_valid=not original_validity)

        result = await DeckRepo.update_deck(setup_deck["test_deck"].id, update_data)

        assert result is not None
        assert result.is_valid == (not original_validity)
        assert result.name == setup_deck["test_deck"].name

    async def test_update_deck_empty_update(self, setup_deck):
        """Test update with no fields provided."""
        update_data = DeckUpdate()

        result = await DeckRepo.update_deck(setup_deck["test_deck"].id, update_data)

        assert result is not None
        # All fields should remain unchanged
        assert result.name == setup_deck["test_deck"].name
        assert result.description == setup_deck["test_deck"].description
        assert result.is_valid == setup_deck["test_deck"].is_valid

    async def test_update_deck_not_found(self, init_db):
        """Test updating non-existent deck returns None."""
        non_existent_id = 99999
        update_data = DeckUpdate(name="New Name")

        result = await DeckRepo.update_deck(non_existent_id, update_data)

        assert result is None


@pytest.mark.asyncio
@pytest.mark.asyncio
class TestDeckRepoDelete:
    """Integration tests for DeckRepo delete operations."""

    async def test_delete_deck_success(self, setup_deck):
        """Test successful deck deletion."""
        deck = setup_deck["test_deck"]
        deck_id = deck.id
        deck_db = Deck.get(id=deck_id)
        assert deck_db is not None

        result = await DeckRepo.delete_deck(deck_id)

        assert result is True

        # Verify deck is actually deleted
        deleted_deck = await DeckRepo.get_deck(deck_id)
        assert deleted_deck is None
        with pytest.raises(DoesNotExist):
            deleted_deck_db = await Deck.get(id=deck_id)

    async def test_delete_deck_not_found(self, init_db):
        """Test deleting non-existent deck returns False."""
        non_existent_id = 99999

        result = await DeckRepo.delete_deck(non_existent_id)

        assert result is False

    async def test_delete_deck_multiple_times(self, setup_deck):
        """Test deleting same deck multiple times."""
        # First deletion should succeed
        result1 = await DeckRepo.delete_deck(setup_deck["test_deck"].id)
        assert result1 is True

        # Second deletion should fail
        result2 = await DeckRepo.delete_deck(setup_deck["test_deck"].id)
        assert result2 is False


@pytest.mark.asyncio
@pytest.mark.asyncio
class TestDeckRepoEdgeCases:
    """Integration tests for DeckRepo edge cases and error conditions."""

    async def test_create_deck_with_very_long_name(self, init_db, setup_owner):
        """Test creating deck with maximum length name."""
        long_name = "A" * 255  # Maximum length according to model
        deck_create = DeckCreate(name=long_name, owner=setup_owner)

        result = await DeckRepo.create_deck_record(deck_create)

        assert result.name == long_name
        assert len(result.name) == 255

    async def test_create_deck_with_very_long_description(self, init_db, setup_owner):
        """Test creating deck with very long description."""
        long_description = "This is a very long description. " * 100
        deck_create = DeckCreate(
            name="Long Description Deck",
            description=long_description,
            owner=setup_owner,
        )

        result = await DeckRepo.create_deck_record(deck_create)

        assert result.description == long_description
        assert result.name == "Long Description Deck"

    async def test_create_deck_with_empty_description_string(self, init_db, setup_owner):
        """Test creating deck with empty string as description."""
        deck_create = DeckCreate(
            name="Empty Description Deck", description="", owner=setup_owner
        )

        result = await DeckRepo.create_deck_record(deck_create)

        assert result.description == ""
        assert result.name == "Empty Description Deck"

    async def test_deck_id_autoincrement(self, init_db, setup_owner):
        """Test that deck IDs are properly auto-incremented."""
        deck1 = await DeckRepo.create_deck_record(
            DeckCreate(name="Deck 1", owner=setup_owner)
        )
        deck2 = await DeckRepo.create_deck_record(
            DeckCreate(name="Deck 2", owner=setup_owner)
        )
        deck3 = await DeckRepo.create_deck_record(
            DeckCreate(name="Deck 3", owner=setup_owner)
        )

        # IDs should be different and in ascending order
        assert deck1.id != deck2.id != deck3.id
        assert deck1.id < deck2.id < deck3.id

    async def test_update_deck_duplicate_name_constraint(self, init_db, setup_owner):
        """Test that updating deck to duplicate name fails."""
        # Create two decks
        deck1 = await DeckRepo.create_deck_record(
            DeckCreate(name="First Deck", owner=setup_owner)
        )
        deck2 = await DeckRepo.create_deck_record(
            DeckCreate(name="Second Deck", owner=setup_owner)
        )

        # Try to update deck2 to have same name as deck1
        update_data = DeckUpdate(name="First Deck")

        with pytest.raises(IntegrityError):
            await DeckRepo.update_deck(deck2.id, update_data)

    async def test_deck_owner_relationship_constraint(self, init_db, setup_owner):
        """Test that deck requires valid owner relationship."""
        # Create deck with valid owner
        deck_create = DeckCreate(name="Test Deck", owner=setup_owner)
        deck = await DeckRepo.create_deck_record(deck_create)

        # Verify owner relationship exists
        assert deck.owner_id == setup_owner.id

        # Verify deck can be retrieved with owner relationship
        retrieved_deck = await DeckRepo.get_deck(deck.id)
        assert retrieved_deck.owner_id == setup_owner.id
