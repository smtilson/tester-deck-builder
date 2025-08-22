import pytest
import random
from fast_backend.app.crud.deck_cards import DeckCardRepo
from fast_backend.app.crud.decks import DeckRepo
from fast_backend.app.crud.cards import CardRepo
from fast_backend.app.models.old_deck_cards import DeckCard
from fast_backend.app.schemas.deck_cards import DeckCardCreate, DeckCardUpdate
from fast_backend.app.schemas.decks import DeckCreate
from fast_backend.app.schemas.cards import CardCreate


@pytest.mark.skip("standard")
# @pytest.mark.usefixtures("init_db")
@pytest.mark.asyncio
class TestDeckCardRepoAdd:
    """Integration tests for DeckCardRepo add card to deck operations."""

    async def test_add_card_to_deck_success(self, db, single_deck_and_cards):
        """Test successfully adding a card to a deck."""
        test_deck = single_deck_and_cards["test_deck"]
        test_cards = single_deck_and_cards["test_cards"]
        card = random.choice(test_cards)
        deck_card_create = DeckCardCreate(card_id=card.id, quantity=4)

        result = await DeckCardRepo.add_card_to_deck(test_deck.id, deck_card_create)

        assert result.card_id == card.id
        assert result.deck_id == test_deck.id
        assert result.quantity == 4
        assert isinstance(result.id, int)
        assert result.card.id == card.id
        assert result.card.name == card.name

        # Verify deck_card exists in database
        db_deck_card = await DeckCard.get(id=result.id)
        assert db_deck_card.card_id == card.id
        assert db_deck_card.deck_id == test_deck.id
        assert db_deck_card.quantity == 4

    async def test_add_card_to_deck_default_quantity(self, db, single_deck_and_cards):
        """Test adding card with default quantity of 1."""
        test_deck = single_deck_and_cards["test_deck"]
        test_cards = single_deck_and_cards["test_cards"]
        card = test_cards[1]
        deck_card_create = DeckCardCreate(card_id=card.id)  # Default quantity is 1

        result = await DeckCardRepo.add_card_to_deck(test_deck.id, deck_card_create)

        assert result.quantity == 1
        assert result.card_id == card.id
        assert result.deck_id == test_deck.id

    async def test_add_existing_card_increases_quantity(
        self, db, single_deck_and_cards
    ):
        """Test that adding existing card increases quantity instead of creating duplicate."""
        test_deck = single_deck_and_cards["test_deck"]
        test_cards = single_deck_and_cards["test_cards"]
        card = test_cards[0]
        deck_card_create = DeckCardCreate(card_id=card.id, quantity=2)

        # Add card first time
        result1 = await DeckCardRepo.add_card_to_deck(test_deck.id, deck_card_create)
        assert result1.quantity == 2

        # Add same card again
        result2 = await DeckCardRepo.add_card_to_deck(test_deck.id, deck_card_create)
        assert result2.quantity == 4  # 2 + 2
        assert result2.id == result1.id  # Same record

    async def test_add_multiple_different_cards(self, db, single_deck_and_cards):
        """Test adding multiple different cards to same deck."""
        test_deck = single_deck_and_cards["test_deck"]
        test_cards = single_deck_and_cards["test_cards"]
        card1 = test_cards[0]
        card2 = test_cards[1]

        deck_card1 = DeckCardCreate(card_id=card1.id, quantity=3)
        deck_card2 = DeckCardCreate(card_id=card2.id, quantity=2)

        result1 = await DeckCardRepo.add_card_to_deck(test_deck.id, deck_card1)
        result2 = await DeckCardRepo.add_card_to_deck(test_deck.id, deck_card2)

        assert result1.id != result2.id
        assert result1.card_id == card1.id
        assert result2.card_id == card2.id
        assert result1.quantity == 3
        assert result2.quantity == 2

    async def test_add_card_with_high_quantity(self, db, single_deck_and_cards):
        """Test adding card with high quantity value."""
        test_deck = single_deck_and_cards["test_deck"]
        test_cards = single_deck_and_cards["test_cards"]
        card = test_cards[0]
        deck_card_create = DeckCardCreate(card_id=card.id, quantity=99)

        result = await DeckCardRepo.add_card_to_deck(test_deck.id, deck_card_create)

        assert result.quantity == 99
        assert result.card_id == card.id


@pytest.mark.skip("standard")
@pytest.mark.asyncio
class TestDeckCardRepoGet:
    """Integration tests for DeckCardRepo get operations."""

    async def test_get_cards_for_deck_returns_all(self, db, single_deck_with_cards):
        """Test getting all cards for a deck."""
        test_deck = single_deck_with_cards["test_deck"]
        test_cards = single_deck_with_cards["test_cards"]
        result = await DeckCardRepo.get_cards_for_deck(test_deck.id)

        assert len(result) == 3
        card_ids = [dc.card_id for dc in result]
        expected_card_ids = [card.id for card in test_cards]
        assert set(card_ids) == set(expected_card_ids)

    async def test_get_cards_for_deck_includes_card_details(
        self, db, single_deck_with_cards
    ):
        """Test that get_cards_for_deck includes full card details."""
        test_deck = single_deck_with_cards["test_deck"]
        result = await DeckCardRepo.get_cards_for_deck(test_deck.id)

        for deck_card in result:
            assert hasattr(deck_card, "card")
            assert deck_card.card.id == deck_card.card_id
            assert isinstance(deck_card.card.name, str)
            assert deck_card.card.text is None or isinstance(deck_card.card.text, str)

    async def test_get_cards_for_deck_correct_quantities(
        self, db, single_deck_with_cards
    ):
        """Test that get_cards_for_deck returns correct quantities."""
        test_deck = single_deck_with_cards["test_deck"]
        result = await DeckCardRepo.get_cards_for_deck(test_deck.id)

        # Sort by card_id to ensure consistent order
        result_sorted = sorted(result, key=lambda x: x.card_id)
        expected_quantities = [4, 2, 1]  # Matches setup order

        for i, deck_card in enumerate(result_sorted):
            assert deck_card.quantity == expected_quantities[i]

    async def test_get_cards_for_empty_deck(self, db, single_deck_with_cards):
        """Test getting cards for deck with no cards."""
        owner = single_deck_with_cards["owner"]
        # Create empty deck
        empty_deck_create = DeckCreate(name="Empty Deck", owner=owner)
        empty_deck = await DeckRepo.create_deck_record(empty_deck_create)

        result = await DeckCardRepo.get_cards_for_deck(empty_deck.id)

        assert result == []

    async def test_get_cards_for_nonexistent_deck(self, db, single_deck_with_cards):
        """Test getting cards for non-existent deck."""
        non_existent_deck_id = 99999

        result = await DeckCardRepo.get_cards_for_deck(non_existent_deck_id)

        assert result == []


@pytest.mark.skip("standard")
@pytest.mark.asyncio
class TestDeckCardRepoUpdate:
    """Integration tests for DeckCardRepo update operations."""

    async def test_update_card_quantity_success(self, db, single_deck_card):
        """Test successfully updating card quantity in deck."""
        test_deck_card = single_deck_card["test_deck_card"]
        update_data = DeckCardUpdate(quantity=6)

        result = await DeckCardRepo.update_card_quantity_in_deck(
            test_deck_card.id, update_data
        )

        assert result is not None
        assert result.id == test_deck_card.id
        assert result.quantity == 6
        assert result.card_id == test_deck_card.card_id
        assert result.deck_id == test_deck_card.deck_id

        # Verify update persisted in database
        from fast_backend.app.models.old_deck_cards import DeckCard

        db_deck_card = await DeckCard.get(id=test_deck_card.id)
        assert db_deck_card.quantity == 6

    async def test_update_card_quantity_to_zero(self, db, single_deck_card):
        """Test updating card quantity to zero (but not removing)."""
        test_deck_card = single_deck_card["test_deck_card"]
        update_data = DeckCardUpdate(quantity=0)

        result = await DeckCardRepo.update_card_quantity_in_deck(
            test_deck_card.id, update_data
        )

        assert result is not None
        assert result.quantity == 0
        assert result.id == test_deck_card.id

    async def test_update_card_quantity_to_high_value(self, db, single_deck_card):
        """Test updating card quantity to high value."""
        test_deck_card = single_deck_card["test_deck_card"]
        update_data = DeckCardUpdate(quantity=999)

        result = await DeckCardRepo.update_card_quantity_in_deck(
            test_deck_card.id, update_data
        )

        assert result is not None
        assert result.quantity == 999

    async def test_update_card_quantity_empty_update(self, db, single_deck_card):
        """Test update with no fields provided."""
        test_deck_card = single_deck_card["test_deck_card"]
        update_data = DeckCardUpdate()

        result = await DeckCardRepo.update_card_quantity_in_deck(
            test_deck_card.id, update_data
        )

        assert result is not None
        # Quantity should remain unchanged
        assert result.quantity == test_deck_card.quantity

    async def test_update_card_quantity_includes_card_details(
        self, db, single_deck_card
    ):
        """Test that update result includes full card details."""
        test_deck_card = single_deck_card["test_deck_card"]
        test_card = single_deck_card["test_card"]
        update_data = DeckCardUpdate(quantity=8)

        result = await DeckCardRepo.update_card_quantity_in_deck(
            test_deck_card.id, update_data
        )

        assert result is not None
        assert hasattr(result, "card")
        assert result.card.id == test_card.id
        assert result.card.name == test_card.name

    async def test_update_nonexistent_deck_card(self, db, single_deck_card):
        """Test updating non-existent deck card returns None."""
        non_existent_id = 99999
        update_data = DeckCardUpdate(quantity=5)

        result = await DeckCardRepo.update_card_quantity_in_deck(
            non_existent_id, update_data
        )

        assert result is None


@pytest.mark.skip("standard")
@pytest.mark.asyncio
class TestDeckCardRepoRemove:
    """Integration tests for DeckCardRepo remove operations."""

    async def test_remove_card_from_deck_success(self, db, single_deck_card):
        """Test successfully removing card from deck."""
        test_deck_card = single_deck_card["test_deck_card"]
        test_deck = single_deck_card["test_deck"]
        result = await DeckCardRepo.remove_card_from_deck(test_deck_card.id)

        assert result is True

        # Verify card is actually removed
        remaining_cards = await DeckCardRepo.get_cards_for_deck(test_deck.id)
        assert len(remaining_cards) == 0

        # Verify deck_card no longer exists in database
        from fast_backend.app.models.old_deck_cards import DeckCard
        from tortoise.exceptions import DoesNotExist

        with pytest.raises(DoesNotExist):
            await DeckCard.get(id=test_deck_card.id)

    async def test_remove_nonexistent_deck_card(self, db, single_deck_card):
        """Test removing non-existent deck card returns False."""
        non_existent_id = 99999

        result = await DeckCardRepo.remove_card_from_deck(non_existent_id)

        assert result is False

    async def test_remove_card_multiple_times(self, db, single_deck_card):
        """Test removing same deck card multiple times."""
        test_deck_card = single_deck_card["test_deck_card"]
        # First removal should succeed
        result1 = await DeckCardRepo.remove_card_from_deck(test_deck_card.id)
        assert result1 is True

        # Second removal should fail
        result2 = await DeckCardRepo.remove_card_from_deck(test_deck_card.id)
        assert result2 is False

    async def test_remove_card_preserves_other_cards(
        self, db, single_deck_card, card_test_data
    ):
        """Test that removing one card preserves other cards in deck."""
        test_deck_card = single_deck_card["test_deck_card"]
        test_deck = single_deck_card["test_deck"]

        # Add another card to deck
        card_data = card_test_data[1]  # Giant Growth
        card_create = CardCreate(name=card_data["name"], text=card_data["text"])
        another_card = await CardRepo.create_card(card_create)

        deck_card_create = DeckCardCreate(card_id=another_card.id, quantity=2)
        another_deck_card = await DeckCardRepo.add_card_to_deck(
            test_deck.id, deck_card_create
        )

        # Remove first card
        result = await DeckCardRepo.remove_card_from_deck(test_deck_card.id)
        assert result is True

        # Verify second card is still there
        remaining_cards = await DeckCardRepo.get_cards_for_deck(test_deck.id)
        assert len(remaining_cards) == 1
        assert remaining_cards[0].id == another_deck_card.id
        assert remaining_cards[0].card_id == another_card.id


@pytest.mark.skip("special")
@pytest.mark.asyncio
class TestDeckCardRepoEdgeCases:
    """Integration tests for DeckCardRepo edge cases and error conditions."""

    async def test_add_card_with_zero_quantity(self, db, single_deck_and_cards):
        """Test adding card with zero quantity."""
        test_deck = single_deck_and_cards["test_deck"]
        test_cards = single_deck_and_cards["test_cards"]
        test_card = test_cards[0]
        deck_card_create = DeckCardCreate(card_id=test_card.id, quantity=0)

        result = await DeckCardRepo.add_card_to_deck(test_deck.id, deck_card_create)

        assert result.quantity == 0
        assert result.card_id == test_card.id

    async def test_add_card_quantity_accumulation_multiple_additions(
        self, db, single_deck_and_cards
    ):
        """Test that quantity accumulates correctly over multiple additions."""
        test_deck = single_deck_and_cards["test_deck"]
        test_cards = single_deck_and_cards["test_cards"]
        test_card = test_cards[0]
        deck_card_create = DeckCardCreate(card_id=test_card.id, quantity=3)

        # Add card multiple times
        result1 = await DeckCardRepo.add_card_to_deck(test_deck.id, deck_card_create)
        assert result1.quantity == 3

        result2 = await DeckCardRepo.add_card_to_deck(test_deck.id, deck_card_create)
        assert result2.quantity == 6

        result3 = await DeckCardRepo.add_card_to_deck(test_deck.id, deck_card_create)
        assert result3.quantity == 9

        # All results should be the same record
        assert result1.id == result2.id == result3.id

    async def test_deck_card_unique_constraint(self, db, single_deck_and_cards):
        """Test that deck-card combination maintains uniqueness."""
        test_deck = single_deck_and_cards["test_deck"]
        test_cards = single_deck_and_cards["test_cards"]
        test_card = test_cards[0]
        # Add card to deck
        deck_card_create = DeckCardCreate(card_id=test_card.id, quantity=1)
        result1 = await DeckCardRepo.add_card_to_deck(test_deck.id, deck_card_create)

        # Add same card again - should update existing record, not create new one
        result2 = await DeckCardRepo.add_card_to_deck(test_deck.id, deck_card_create)

        assert result1.id == result2.id
        assert result2.quantity == 2

        # Verify only one record exists
        cards_in_deck = await DeckCardRepo.get_cards_for_deck(test_deck.id)
        assert len(cards_in_deck) == 1

    async def test_operations_with_nonexistent_card_id(self, db, single_deck_and_cards):
        """Test operations with non-existent card ID."""
        test_deck = single_deck_and_cards["test_deck"]
        non_existent_card_id = 99999
        deck_card_create = DeckCardCreate(card_id=non_existent_card_id, quantity=1)

        # This should fail due to foreign key constraint
        with pytest.raises(Exception):  # Could be IntegrityError or similar
            await DeckCardRepo.add_card_to_deck(test_deck.id, deck_card_create)

    async def test_operations_with_nonexistent_deck_id(self, db, single_deck_and_cards):
        """Test operations with non-existent deck ID."""
        test_cards = single_deck_and_cards["test_cards"]
        test_card = test_cards[0]
        non_existent_deck_id = 99999
        deck_card_create = DeckCardCreate(card_id=test_card.id, quantity=1)

        # This should fail due to foreign key constraint
        with pytest.raises(Exception):  # Could be IntegrityError or similar
            await DeckCardRepo.add_card_to_deck(non_existent_deck_id, deck_card_create)
