import pytest
import pytest_asyncio
import uuid
from tortoise.exceptions import IntegrityError

from fast_backend.app.crud.decks import DeckRepo
from fast_backend.app.crud.users import UserRepo
from fast_backend.app.schemas.decks import DeckCreate, DeckUpdate
from fast_backend.app.schemas.users import UserCreate, UserResponse


@pytest.mark.usefixtures("init_db")
class TestDeckRepoCreate:
    """Integration tests for DeckRepo create operations."""

    @pytest_asyncio.fixture(autouse=True)
    async def setup_owner(self, init_db, all_test_data):
        """Create a test user to own decks."""
        user_data = all_test_data.get_user_by_username("testuser1")
        user_create = UserCreate(**user_data)
        owner = await UserRepo.create_user(user_create)
        return owner

    @pytest.mark.asyncio
    async def test_create_deck_success(self, all_test_data, setup_owner):
        """Test successful deck creation with valid data."""
        deck_data = all_test_data.get_deck_by_name("Red Burn Deck")
        deck_create = DeckCreate(
            name=deck_data["name"],
            description=deck_data["description"],
            is_valid=deck_data["is_valid"],
            owner=setup_owner
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
        from fast_backend.app.models.decks import Deck
        db_deck = await Deck.get(id=result.id)
        assert db_deck.name == deck_data["name"]
        assert db_deck.description == deck_data["description"]
        assert db_deck.is_valid == deck_data["is_valid"]
        assert db_deck.owner_id == setup_owner.id

    @pytest.mark.asyncio
    async def test_create_deck_with_null_description(self, setup_owner):
        """Test creating deck with null description."""
        deck_create = DeckCreate(
            name="Deck Without Description",
            description=None,
            is_valid=False,
            owner=setup_owner
        )
        
        result = await DeckRepo.create_deck_record(deck_create)
        
        assert result.name == "Deck Without Description"
        assert result.description is None
        assert result.is_valid is False
        assert result.owner_id == setup_owner.id

    @pytest.mark.asyncio
    async def test_create_deck_minimal_data(self, setup_owner):
        """Test creating deck with minimal required data."""
        deck_create = DeckCreate(
            name="Minimal Deck",
            owner=setup_owner
        )
        
        result = await DeckRepo.create_deck_record(deck_create)
        
        assert result.name == "Minimal Deck"
        assert result.description is None
        assert result.is_valid is False  # Default value
        assert result.owner_id == setup_owner.id

    @pytest.mark.asyncio
    async def test_create_deck_duplicate_name_fails(self, setup_owner):
        """Test that creating deck with duplicate name fails."""
        deck_create = DeckCreate(
            name="Unique Deck Name",
            owner=setup_owner
        )
        
        # Create first deck
        await DeckRepo.create_deck_record(deck_create)
        
        # Attempt to create second deck with same name should fail
        with pytest.raises(IntegrityError):
            await DeckRepo.create_deck_record(deck_create)

    @pytest.mark.asyncio
    async def test_create_multiple_decks_different_names(self, setup_owner):
        """Test creating multiple decks with different names succeeds."""
        deck1 = DeckCreate(name="First Deck", owner=setup_owner)
        deck2 = DeckCreate(name="Second Deck", owner=setup_owner)
        
        result1 = await DeckRepo.create_deck_record(deck1)
        result2 = await DeckRepo.create_deck_record(deck2)
        
        assert result1.id != result2.id
        assert result1.name == "First Deck"
        assert result2.name == "Second Deck"
        assert result1.owner_id == result2.owner_id == setup_owner.id


@pytest.mark.usefixtures("init_db")
class TestDeckRepoRead:
    """Integration tests for DeckRepo read operations."""

    @pytest_asyncio.fixture(autouse=True)
    async def setup_decks(self, init_db, all_test_data):
        """Create test decks for read operations."""
        # Create owners first
        user1_data = all_test_data.get_user_by_username("testuser1")
        user2_data = all_test_data.get_user_by_username("admin_user")
        owner1 = await UserRepo.create_user(UserCreate(**user1_data))
        owner2 = await UserRepo.create_user(UserCreate(**user2_data))
        
        # Create decks
        created_decks = []
        for deck_data in all_test_data.deck_data:
            owner = owner1 if deck_data["owner_id"] == user1_data["id"] else owner2
            deck_create = DeckCreate(
                name=deck_data["name"],
                description=deck_data["description"],
                is_valid=deck_data["is_valid"],
                owner=owner
            )
            created_deck = await DeckRepo.create_deck_record(deck_create)
            created_decks.append(created_deck)
        return created_decks

    @pytest.mark.asyncio
    async def test_get_deck_by_id_success(self, setup_decks):
        """Test successful retrieval of deck by ID."""
        created_deck = setup_decks[0]
        
        result = await DeckRepo.get_deck(created_deck.id)
        
        assert result is not None
        assert result.id == created_deck.id
        assert result.name == created_deck.name
        assert result.description == created_deck.description
        assert result.is_valid == created_deck.is_valid
        assert result.owner_id == created_deck.owner_id

    @pytest.mark.asyncio
    async def test_get_deck_by_id_not_found(self):
        """Test that getting non-existent deck returns None."""
        non_existent_id = 99999
        
        result = await DeckRepo.get_deck(non_existent_id)
        
        assert result is None

    @pytest.mark.asyncio
    async def test_get_all_decks_returns_all(self, deck_test_data):
        """Test that get_all_decks returns all created decks."""
        result = await DeckRepo.get_all_decks()
        
        assert len(result) == len(deck_test_data)
        deck_names = [deck.name for deck in result]
        expected_names = [deck["name"] for deck in deck_test_data]
        assert set(deck_names) == set(expected_names)

    @pytest.mark.asyncio
    async def test_get_all_decks_empty_database(self):
        """Test get_all_decks with empty database."""
        # Clear all decks
        from fast_backend.app.models.decks import Deck
        await Deck.all().delete()
        
        result = await DeckRepo.get_all_decks()
        
        assert result == []

    @pytest.mark.asyncio
    async def test_get_all_decks_maintains_properties(self):
        """Test that get_all_decks returns decks with all properties intact."""
        result = await DeckRepo.get_all_decks()
        
        for deck in result:
            assert isinstance(deck.id, int)
            assert isinstance(deck.name, str)
            assert deck.description is None or isinstance(deck.description, str)
            assert isinstance(deck.is_valid, bool)
            assert isinstance(deck.owner_id, uuid.UUID)
            assert deck.created_at is not None
            assert deck.updated_at is not None


@pytest.mark.usefixtures("init_db")
class TestDeckRepoUpdate:
    """Integration tests for DeckRepo update operations."""

    @pytest_asyncio.fixture(autouse=True)
    async def setup_deck(self, init_db, all_test_data):
        """Create a test deck for update operations."""
        user_data = all_test_data.get_user_by_username("testuser1")
        owner = await UserRepo.create_user(UserCreate(**user_data))
        
        deck_data = all_test_data.get_deck_by_name("Red Burn Deck")
        deck_create = DeckCreate(
            name=deck_data["name"],
            description=deck_data["description"],
            is_valid=deck_data["is_valid"],
            owner=owner
        )
        test_deck = await DeckRepo.create_deck_record(deck_create)
        return {"owner": owner, "test_deck": test_deck}

    @pytest.mark.asyncio
    async def test_update_deck_success(self, all_test_data, setup_deck):
        """Test successful deck update."""
        new_owner = await UserRepo.create_user(UserCreate(**all_test_data.get_user_by_username("admin_user")))
        update_data = DeckUpdate(
            name="Updated Red Burn Deck",
            description="Updated description for the burn deck",
            is_valid=True,
            owner=new_owner
        )
        
        result = await DeckRepo.update_deck(setup_deck["test_deck"].id, update_data)
        
        assert result is not None
        assert result.id == setup_deck["test_deck"].id
        assert result.name == "Updated Red Burn Deck"
        assert result.description == "Updated description for the burn deck"
        assert result.is_valid is True
        # Owner should remain unchanged as update_deck doesn't change owner
        assert result.owner_id == setup_deck["test_deck"].owner_id
        
        # Verify update persisted in database
        from fast_backend.app.models.decks import Deck
        db_deck = await Deck.get(id=setup_deck["test_deck"].id)
        assert db_deck.name == "Updated Red Burn Deck"
        assert db_deck.description == "Updated description for the burn deck"
        assert db_deck.is_valid is True

    @pytest.mark.asyncio
    async def test_update_deck_partial_name_only(self):
        """Test partial deck update with only name field."""
        update_data = DeckUpdate(name="Only Name Changed")
        
        result = await DeckRepo.update_deck(self.test_deck.id, update_data)
        
        assert result is not None
        assert result.name == "Only Name Changed"
        # Other fields should remain unchanged
        assert result.description == self.test_deck.description
        assert result.is_valid == self.test_deck.is_valid

    @pytest.mark.asyncio
    async def test_update_deck_partial_description_only(self):
        """Test partial deck update with only description field."""
        update_data = DeckUpdate(description="Only description changed")
        
        result = await DeckRepo.update_deck(self.test_deck.id, update_data)
        
        assert result is not None
        assert result.description == "Only description changed"
        # Other fields should remain unchanged
        assert result.name == self.test_deck.name
        assert result.is_valid == self.test_deck.is_valid

    @pytest.mark.asyncio
    async def test_update_deck_set_description_to_null(self):
        """Test updating deck description to null."""
        update_data = DeckUpdate(description=None)
        
        result = await DeckRepo.update_deck(self.test_deck.id, update_data)
        
        assert result is not None
        assert result.description is None
        assert result.name == self.test_deck.name

    @pytest.mark.asyncio
    async def test_update_deck_toggle_validity(self):
        """Test updating deck validity status."""
        original_validity = self.test_deck.is_valid
        update_data = DeckUpdate(is_valid=not original_validity)
        
        result = await DeckRepo.update_deck(self.test_deck.id, update_data)
        
        assert result is not None
        assert result.is_valid == (not original_validity)
        assert result.name == self.test_deck.name

    @pytest.mark.asyncio
    async def test_update_deck_empty_update(self):
        """Test update with no fields provided."""
        update_data = DeckUpdate()
        
        result = await DeckRepo.update_deck(self.test_deck.id, update_data)
        
        assert result is not None
        # All fields should remain unchanged
        assert result.name == self.test_deck.name
        assert result.description == self.test_deck.description
        assert result.is_valid == self.test_deck.is_valid

    @pytest.mark.asyncio
    async def test_update_deck_not_found(self):
        """Test updating non-existent deck returns None."""
        non_existent_id = 99999
        update_data = DeckUpdate(name="New Name")
        
        result = await DeckRepo.update_deck(non_existent_id, update_data)
        
        assert result is None


class TestDeckRepoDelete:
    """Integration tests for DeckRepo delete operations."""

    @pytest_asyncio.fixture(autouse=True)
    async def setup_deck(self, init_db, all_test_data):
        """Create a test deck for delete operations."""
        user_data = all_test_data.get_user_by_username("testuser1")
        self.owner = await UserRepo.create_user(UserCreate(**user_data))
        
        deck_data = all_test_data.get_deck_by_name("Red Burn Deck")
        deck_create = DeckCreate(
            name=deck_data["name"],
            description=deck_data["description"],
            is_valid=deck_data["is_valid"],
            owner=self.owner
        )
        self.test_deck = await DeckRepo.create_deck_record(deck_create)

    @pytest.mark.asyncio
    async def test_delete_deck_success(self):
        """Test successful deck deletion."""
        result = await DeckRepo.delete_deck(self.test_deck.id)
        
        assert result is True
        
        # Verify deck is actually deleted
        deleted_deck = await DeckRepo.get_deck(self.test_deck.id)
        assert deleted_deck is None
        
        # Verify deck no longer exists in database
        from fast_backend.app.models.decks import Deck
        from tortoise.exceptions import DoesNotExist
        with pytest.raises(DoesNotExist):
            await Deck.get(id=self.test_deck.id)

    @pytest.mark.asyncio
    async def test_delete_deck_not_found(self):
        """Test deleting non-existent deck returns False."""
        non_existent_id = 99999
        
        result = await DeckRepo.delete_deck(non_existent_id)
        
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_deck_multiple_times(self):
        """Test deleting same deck multiple times."""
        # First deletion should succeed
        result1 = await DeckRepo.delete_deck(self.test_deck.id)
        assert result1 is True
        
        # Second deletion should fail
        result2 = await DeckRepo.delete_deck(self.test_deck.id)
        assert result2 is False


class TestDeckRepoEdgeCases:
    """Integration tests for DeckRepo edge cases and error conditions."""

    @pytest_asyncio.fixture(autouse=True)
    async def setup_owner(self, init_db, all_test_data):
        """Create a test user to own decks."""
        user_data = all_test_data.get_user_by_username("testuser1")
        user_create = UserCreate(**user_data)
        self.owner = await UserRepo.create_user(user_create)

    @pytest.mark.asyncio
    async def test_create_deck_with_very_long_name(self):
        """Test creating deck with maximum length name."""
        long_name = "A" * 255  # Maximum length according to model
        deck_create = DeckCreate(name=long_name, owner=self.owner)
        
        result = await DeckRepo.create_deck_record(deck_create)
        
        assert result.name == long_name
        assert len(result.name) == 255

    @pytest.mark.asyncio
    async def test_create_deck_with_very_long_description(self):
        """Test creating deck with very long description."""
        long_description = "This is a very long description. " * 100
        deck_create = DeckCreate(
            name="Long Description Deck",
            description=long_description,
            owner=self.owner
        )
        
        result = await DeckRepo.create_deck_record(deck_create)
        
        assert result.description == long_description
        assert result.name == "Long Description Deck"

    @pytest.mark.asyncio
    async def test_create_deck_with_empty_description_string(self):
        """Test creating deck with empty string as description."""
        deck_create = DeckCreate(
            name="Empty Description Deck",
            description="",
            owner=self.owner
        )
        
        result = await DeckRepo.create_deck_record(deck_create)
        
        assert result.description == ""
        assert result.name == "Empty Description Deck"

    @pytest.mark.asyncio
    async def test_deck_id_autoincrement(self):
        """Test that deck IDs are properly auto-incremented."""
        deck1 = await DeckRepo.create_deck_record(DeckCreate(name="Deck 1", owner=self.owner))
        deck2 = await DeckRepo.create_deck_record(DeckCreate(name="Deck 2", owner=self.owner))
        deck3 = await DeckRepo.create_deck_record(DeckCreate(name="Deck 3", owner=self.owner))
        
        # IDs should be different and in ascending order
        assert deck1.id != deck2.id != deck3.id
        assert deck1.id < deck2.id < deck3.id

    @pytest.mark.asyncio
    async def test_update_deck_duplicate_name_constraint(self):
        """Test that updating deck to duplicate name fails."""
        # Create two decks
        deck1 = await DeckRepo.create_deck_record(DeckCreate(name="First Deck", owner=self.owner))
        deck2 = await DeckRepo.create_deck_record(DeckCreate(name="Second Deck", owner=self.owner))
        
        # Try to update deck2 to have same name as deck1
        update_data = DeckUpdate(name="First Deck")
        
        with pytest.raises(IntegrityError):
            await DeckRepo.update_deck(deck2.id, update_data)

    @pytest.mark.asyncio
    async def test_deck_owner_relationship_constraint(self):
        """Test that deck requires valid owner relationship."""
        # Create deck with valid owner
        deck_create = DeckCreate(name="Test Deck", owner=self.owner)
        deck = await DeckRepo.create_deck_record(deck_create)
        
        # Verify owner relationship exists
        assert deck.owner_id == self.owner.id
        
        # Verify deck can be retrieved with owner relationship
        retrieved_deck = await DeckRepo.get_deck(deck.id)
        assert retrieved_deck.owner_id == self.owner.id
