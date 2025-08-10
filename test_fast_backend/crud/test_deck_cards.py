import pytest

from fast_backend.app.crud.deck_cards import DeckCardRepo
from fast_backend.app.crud.decks import DeckRepo
from fast_backend.app.crud.cards import CardRepo
from fast_backend.app.crud.users import UserRepo
from fast_backend.app.schemas.deck_cards import DeckCardCreate, DeckCardUpdate
from fast_backend.app.schemas.decks import DeckCreate
from fast_backend.app.schemas.cards import CardCreate
from fast_backend.app.schemas.users import UserCreate
from test_fast_backend.base_class import BaseTestData


class TestDeckCardRepoAdd(BaseTestData):
    """Integration tests for DeckCardRepo add card to deck operations."""

    @pytest.fixture(autouse=True)
    async def setup_deck_and_cards(self):
        """Create test deck and cards for deck_card operations."""
        # Create user
        user_data = self.get_user_by_username("testuser1")
        self.owner = await UserRepo.create_user(UserCreate(**user_data))
        
        # Create deck
        deck_data = self.get_deck_by_name("Red Burn Deck")
        deck_create = DeckCreate(
            name=deck_data["name"],
            description=deck_data["description"],
            is_valid=deck_data["is_valid"],
            owner=self.owner
        )
        self.test_deck = await DeckRepo.create_deck_record(deck_create)
        
        # Create cards
        self.test_cards = []
        for card_data in self.card_data:
            card_create = CardCreate(name=card_data["name"], text=card_data["text"])
            created_card = await CardRepo.create_card(card_create)
            self.test_cards.append(created_card)

    @pytest.mark.asyncio
    async def test_add_card_to_deck_success(self):
        """Test successfully adding a card to a deck."""
        card = self.test_cards[0]
        deck_card_create = DeckCardCreate(card_id=card.id, quantity=4)
        
        result = await DeckCardRepo.add_card_to_deck(self.test_deck.id, deck_card_create)
        
        assert result.card_id == card.id
        assert result.deck_id == self.test_deck.id
        assert result.quantity == 4
        assert isinstance(result.id, int)
        assert result.card.id == card.id
        assert result.card.name == card.name

    @pytest.mark.asyncio
    async def test_add_card_to_deck_default_quantity(self):
        """Test adding card with default quantity of 1."""
        card = self.test_cards[1]
        deck_card_create = DeckCardCreate(card_id=card.id)  # Default quantity is 1
        
        result = await DeckCardRepo.add_card_to_deck(self.test_deck.id, deck_card_create)
        
        assert result.quantity == 1
        assert result.card_id == card.id
        assert result.deck_id == self.test_deck.id

    @pytest.mark.asyncio
    async def test_add_existing_card_increases_quantity(self):
        """Test that adding existing card increases quantity instead of creating duplicate."""
        card = self.test_cards[0]
        deck_card_create = DeckCardCreate(card_id=card.id, quantity=2)
        
        # Add card first time
        result1 = await DeckCardRepo.add_card_to_deck(self.test_deck.id, deck_card_create)
        assert result1.quantity == 2
        
        # Add same card again
        result2 = await DeckCardRepo.add_card_to_deck(self.test_deck.id, deck_card_create)
        assert result2.quantity == 4  # 2 + 2
        assert result2.id == result1.id  # Same record

    @pytest.mark.asyncio
    async def test_add_multiple_different_cards(self):
        """Test adding multiple different cards to same deck."""
        card1 = self.test_cards[0]
        card2 = self.test_cards[1]
        
        deck_card1 = DeckCardCreate(card_id=card1.id, quantity=3)
        deck_card2 = DeckCardCreate(card_id=card2.id, quantity=2)
        
        result1 = await DeckCardRepo.add_card_to_deck(self.test_deck.id, deck_card1)
        result2 = await DeckCardRepo.add_card_to_deck(self.test_deck.id, deck_card2)
        
        assert result1.id != result2.id
        assert result1.card_id == card1.id
        assert result2.card_id == card2.id
        assert result1.quantity == 3
        assert result2.quantity == 2

    @pytest.mark.asyncio
    async def test_add_card_with_high_quantity(self):
        """Test adding card with high quantity value."""
        card = self.test_cards[0]
        deck_card_create = DeckCardCreate(card_id=card.id, quantity=99)
        
        result = await DeckCardRepo.add_card_to_deck(self.test_deck.id, deck_card_create)
        
        assert result.quantity == 99
        assert result.card_id == card.id


class TestDeckCardRepoGet(BaseTestData):
    """Integration tests for DeckCardRepo get operations."""

    @pytest.fixture(autouse=True)
    async def setup_deck_with_cards(self):
        """Create test deck with cards for get operations."""
        # Create user and deck
        user_data = self.get_user_by_username("testuser1")
        self.owner = await UserRepo.create_user(UserCreate(**user_data))
        
        deck_data = self.get_deck_by_name("Red Burn Deck")
        deck_create = DeckCreate(
            name=deck_data["name"],
            description=deck_data["description"],
            is_valid=deck_data["is_valid"],
            owner=self.owner
        )
        self.test_deck = await DeckRepo.create_deck_record(deck_create)
        
        # Create cards
        self.test_cards = []
        for card_data in self.card_data[:3]:  # Use first 3 cards
            card_create = CardCreate(name=card_data["name"], text=card_data["text"])
            created_card = await CardRepo.create_card(card_create)
            self.test_cards.append(created_card)
        
        # Add cards to deck
        self.deck_cards = []
        quantities = [4, 2, 1]
        for i, card in enumerate(self.test_cards):
            deck_card_create = DeckCardCreate(card_id=card.id, quantity=quantities[i])
            deck_card = await DeckCardRepo.add_card_to_deck(self.test_deck.id, deck_card_create)
            self.deck_cards.append(deck_card)

    @pytest.mark.asyncio
    async def test_get_cards_for_deck_returns_all(self):
        """Test getting all cards for a deck."""
        result = await DeckCardRepo.get_cards_for_deck(self.test_deck.id)
        
        assert len(result) == 3
        card_ids = [dc.card_id for dc in result]
        expected_card_ids = [card.id for card in self.test_cards]
        assert set(card_ids) == set(expected_card_ids)

    @pytest.mark.asyncio
    async def test_get_cards_for_deck_includes_card_details(self):
        """Test that get_cards_for_deck includes full card details."""
        result = await DeckCardRepo.get_cards_for_deck(self.test_deck.id)
        
        for deck_card in result:
            assert hasattr(deck_card, 'card')
            assert deck_card.card.id == deck_card.card_id
            assert isinstance(deck_card.card.name, str)
            assert deck_card.card.text is None or isinstance(deck_card.card.text, str)

    @pytest.mark.asyncio
    async def test_get_cards_for_deck_correct_quantities(self):
        """Test that get_cards_for_deck returns correct quantities."""
        result = await DeckCardRepo.get_cards_for_deck(self.test_deck.id)
        
        # Sort by card_id to ensure consistent order
        result_sorted = sorted(result, key=lambda x: x.card_id)
        expected_quantities = [4, 2, 1]  # Matches setup order
        
        for i, deck_card in enumerate(result_sorted):
            assert deck_card.quantity == expected_quantities[i]

    @pytest.mark.asyncio
    async def test_get_cards_for_empty_deck(self):
        """Test getting cards for deck with no cards."""
        # Create empty deck
        empty_deck_create = DeckCreate(name="Empty Deck", owner=self.owner)
        empty_deck = await DeckRepo.create_deck_record(empty_deck_create)
        
        result = await DeckCardRepo.get_cards_for_deck(empty_deck.id)
        
        assert result == []

    @pytest.mark.asyncio
    async def test_get_cards_for_nonexistent_deck(self):
        """Test getting cards for non-existent deck."""
        non_existent_deck_id = 99999
        
        result = await DeckCardRepo.get_cards_for_deck(non_existent_deck_id)
        
        assert result == []


class TestDeckCardRepoUpdate(BaseTestData):
    """Integration tests for DeckCardRepo update operations."""

    @pytest.fixture(autouse=True)
    async def setup_deck_card(self):
        """Create test deck card for update operations."""
        # Create user, deck, and card
        user_data = self.get_user_by_username("testuser1")
        self.owner = await UserRepo.create_user(UserCreate(**user_data))
        
        deck_data = self.get_deck_by_name("Red Burn Deck")
        deck_create = DeckCreate(
            name=deck_data["name"],
            description=deck_data["description"],
            is_valid=deck_data["is_valid"],
            owner=self.owner
        )
        self.test_deck = await DeckRepo.create_deck_record(deck_create)
        
        card_data = self.get_card_by_name("Lightning Bolt")
        card_create = CardCreate(name=card_data["name"], text=card_data["text"])
        self.test_card = await CardRepo.create_card(card_create)
        
        # Add card to deck
        deck_card_create = DeckCardCreate(card_id=self.test_card.id, quantity=4)
        self.test_deck_card = await DeckCardRepo.add_card_to_deck(self.test_deck.id, deck_card_create)

    @pytest.mark.asyncio
    async def test_update_card_quantity_success(self):
        """Test successfully updating card quantity in deck."""
        update_data = DeckCardUpdate(quantity=6)
        
        result = await DeckCardRepo.update_card_quantity_in_deck(
            self.test_deck_card.id, update_data
        )
        
        assert result is not None
        assert result.id == self.test_deck_card.id
        assert result.quantity == 6
        assert result.card_id == self.test_deck_card.card_id
        assert result.deck_id == self.test_deck_card.deck_id

    @pytest.mark.asyncio
    async def test_update_card_quantity_to_zero(self):
        """Test updating card quantity to zero (but not removing)."""
        update_data = DeckCardUpdate(quantity=0)
        
        result = await DeckCardRepo.update_card_quantity_in_deck(
            self.test_deck_card.id, update_data
        )
        
        assert result is not None
        assert result.quantity == 0
        assert result.id == self.test_deck_card.id

    @pytest.mark.asyncio
    async def test_update_card_quantity_to_high_value(self):
        """Test updating card quantity to high value."""
        update_data = DeckCardUpdate(quantity=999)
        
        result = await DeckCardRepo.update_card_quantity_in_deck(
            self.test_deck_card.id, update_data
        )
        
        assert result is not None
        assert result.quantity == 999

    @pytest.mark.asyncio
    async def test_update_card_quantity_empty_update(self):
        """Test update with no fields provided."""
        update_data = DeckCardUpdate()
        
        result = await DeckCardRepo.update_card_quantity_in_deck(
            self.test_deck_card.id, update_data
        )
        
        assert result is not None
        # Quantity should remain unchanged
        assert result.quantity == self.test_deck_card.quantity

    @pytest.mark.asyncio
    async def test_update_card_quantity_includes_card_details(self):
        """Test that update result includes full card details."""
        update_data = DeckCardUpdate(quantity=8)
        
        result = await DeckCardRepo.update_card_quantity_in_deck(
            self.test_deck_card.id, update_data
        )
        
        assert result is not None
        assert hasattr(result, 'card')
        assert result.card.id == self.test_card.id
        assert result.card.name == self.test_card.name

    @pytest.mark.asyncio
    async def test_update_nonexistent_deck_card(self):
        """Test updating non-existent deck card returns None."""
        non_existent_id = 99999
        update_data = DeckCardUpdate(quantity=5)
        
        result = await DeckCardRepo.update_card_quantity_in_deck(
            non_existent_id, update_data
        )
        
        assert result is None


class TestDeckCardRepoRemove(BaseTestData):
    """Integration tests for DeckCardRepo remove operations."""

    @pytest.fixture(autouse=True)
    async def setup_deck_card(self):
        """Create test deck card for remove operations."""
        # Create user, deck, and card
        user_data = self.get_user_by_username("testuser1")
        self.owner = await UserRepo.create_user(UserCreate(**user_data))
        
        deck_data = self.get_deck_by_name("Red Burn Deck")
        deck_create = DeckCreate(
            name=deck_data["name"],
            description=deck_data["description"],
            is_valid=deck_data["is_valid"],
            owner=self.owner
        )
        self.test_deck = await DeckRepo.create_deck_record(deck_create)
        
        card_data = self.get_card_by_name("Lightning Bolt")
        card_create = CardCreate(name=card_data["name"], text=card_data["text"])
        self.test_card = await CardRepo.create_card(card_create)
        
        # Add card to deck
        deck_card_create = DeckCardCreate(card_id=self.test_card.id, quantity=4)
        self.test_deck_card = await DeckCardRepo.add_card_to_deck(self.test_deck.id, deck_card_create)

    @pytest.mark.asyncio
    async def test_remove_card_from_deck_success(self):
        """Test successfully removing card from deck."""
        result = await DeckCardRepo.remove_card_from_deck(self.test_deck_card.id)
        
        assert result is True
        
        # Verify card is actually removed
        remaining_cards = await DeckCardRepo.get_cards_for_deck(self.test_deck.id)
        assert len(remaining_cards) == 0

    @pytest.mark.asyncio
    async def test_remove_nonexistent_deck_card(self):
        """Test removing non-existent deck card returns False."""
        non_existent_id = 99999
        
        result = await DeckCardRepo.remove_card_from_deck(non_existent_id)
        
        assert result is False

    @pytest.mark.asyncio
    async def test_remove_card_multiple_times(self):
        """Test removing same deck card multiple times."""
        # First removal should succeed
        result1 = await DeckCardRepo.remove_card_from_deck(self.test_deck_card.id)
        assert result1 is True
        
        # Second removal should fail
        result2 = await DeckCardRepo.remove_card_from_deck(self.test_deck_card.id)
        assert result2 is False

    @pytest.mark.asyncio
    async def test_remove_card_preserves_other_cards(self):
        """Test that removing one card preserves other cards in deck."""
        # Add another card to deck
        card_data = self.get_card_by_name("Giant Growth")
        card_create = CardCreate(name=card_data["name"], text=card_data["text"])
        another_card = await CardRepo.create_card(card_create)
        
        deck_card_create = DeckCardCreate(card_id=another_card.id, quantity=2)
        another_deck_card = await DeckCardRepo.add_card_to_deck(self.test_deck.id, deck_card_create)
        
        # Remove first card
        result = await DeckCardRepo.remove_card_from_deck(self.test_deck_card.id)
        assert result is True
        
        # Verify second card is still there
        remaining_cards = await DeckCardRepo.get_cards_for_deck(self.test_deck.id)
        assert len(remaining_cards) == 1
        assert remaining_cards[0].id == another_deck_card.id
        assert remaining_cards[0].card_id == another_card.id


class TestDeckCardRepoEdgeCases(BaseTestData):
    """Integration tests for DeckCardRepo edge cases and error conditions."""

    @pytest.fixture(autouse=True)
    async def setup_deck_and_card(self):
        """Create test deck and card for edge case testing."""
        user_data = self.get_user_by_username("testuser1")
        self.owner = await UserRepo.create_user(UserCreate(**user_data))
        
        deck_data = self.get_deck_by_name("Red Burn Deck")
        deck_create = DeckCreate(
            name=deck_data["name"],
            description=deck_data["description"],
            is_valid=deck_data["is_valid"],
            owner=self.owner
        )
        self.test_deck = await DeckRepo.create_deck_record(deck_create)
        
        card_data = self.get_card_by_name("Lightning Bolt")
        card_create = CardCreate(name=card_data["name"], text=card_data["text"])
        self.test_card = await CardRepo.create_card(card_create)

    @pytest.mark.asyncio
    async def test_add_card_with_zero_quantity(self):
        """Test adding card with zero quantity."""
        deck_card_create = DeckCardCreate(card_id=self.test_card.id, quantity=0)
        
        result = await DeckCardRepo.add_card_to_deck(self.test_deck.id, deck_card_create)
        
        assert result.quantity == 0
        assert result.card_id == self.test_card.id

    @pytest.mark.asyncio
    async def test_add_card_quantity_accumulation_multiple_additions(self):
        """Test that quantity accumulates correctly over multiple additions."""
        deck_card_create = DeckCardCreate(card_id=self.test_card.id, quantity=3)
        
        # Add card multiple times
        result1 = await DeckCardRepo.add_card_to_deck(self.test_deck.id, deck_card_create)
        assert result1.quantity == 3
        
        result2 = await DeckCardRepo.add_card_to_deck(self.test_deck.id, deck_card_create)
        assert result2.quantity == 6
        
        result3 = await DeckCardRepo.add_card_to_deck(self.test_deck.id, deck_card_create)
        assert result3.quantity == 9
        
        # All results should be the same record
        assert result1.id == result2.id == result3.id

    @pytest.mark.asyncio
    async def test_deck_card_unique_constraint(self):
        """Test that deck-card combination maintains uniqueness."""
        # Add card to deck
        deck_card_create = DeckCardCreate(card_id=self.test_card.id, quantity=1)
        result1 = await DeckCardRepo.add_card_to_deck(self.test_deck.id, deck_card_create)
        
        # Add same card again - should update existing record, not create new one
        result2 = await DeckCardRepo.add_card_to_deck(self.test_deck.id, deck_card_create)
        
        assert result1.id == result2.id
        assert result2.quantity == 2
        
        # Verify only one record exists
        cards_in_deck = await DeckCardRepo.get_cards_for_deck(self.test_deck.id)
        assert len(cards_in_deck) == 1

    @pytest.mark.asyncio
    async def test_operations_with_nonexistent_card_id(self):
        """Test operations with non-existent card ID."""
        non_existent_card_id = 99999
        deck_card_create = DeckCardCreate(card_id=non_existent_card_id, quantity=1)
        
        # This should fail due to foreign key constraint
        with pytest.raises(Exception):  # Could be IntegrityError or similar
            await DeckCardRepo.add_card_to_deck(self.test_deck.id, deck_card_create)

    @pytest.mark.asyncio
    async def test_operations_with_nonexistent_deck_id(self):
        """Test operations with non-existent deck ID."""
        non_existent_deck_id = 99999
        deck_card_create = DeckCardCreate(card_id=self.test_card.id, quantity=1)
        
        # This should fail due to foreign key constraint
        with pytest.raises(Exception):  # Could be IntegrityError or similar
            await DeckCardRepo.add_card_to_deck(non_existent_deck_id, deck_card_create)
