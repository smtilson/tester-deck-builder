import pytest

from fast_backend.app.crud.deck_cards import DeckCardRepo as crud
from fast_backend.app.models.deck_cards import DeckCard as DeckCardModel
from fast_backend.app.models.decks import Deck as DeckModel
from fast_backend.app.models.cards import Card as CardModel
from fast_backend.app.schemas.deck_cards import (
    DeckCardCreate,
    DeckCardUpdate,
    DeckCardResponseWithCard,
)

# The conftest.py provides the `initialize_database` fixture (autouse)
# and the necessary factories: `deck_factory`, `card_factory`.


@pytest.mark.skip
@pytest.mark.asyncio
@pytest.mark.usefixtures("initialize_database")
class TestDeckCardCrud:
    """
    Test suite for the DeckCard CRUD functions.
    """

    async def test_add_new_card_to_deck(
        self, initialize_database, deck_factory, card_factory
    ):
        """Verify that a new card can be added to a deck."""
        # Arrange
        deck = await deck_factory({"name": "Test Deck"})
        card = await card_factory({"name": "Test Card"})
        card_data = DeckCardCreate(card_id=card.id, quantity=2)

        # Act
        result = await crud.add_card_to_deck(deck.id, card_data)

        # Assert (1): Check the returned object from the CRUD function
        assert isinstance(result, DeckCardResponseWithCard)
        assert result.deck_id == deck.id
        assert result.card.id == card.id
        assert result.quantity == 2

        # Assert (2): Check the DeckCard table directly
        db_link = await DeckCardModel.get_or_none(deck_id=deck.id, card_id=card.id)
        assert db_link is not None
        assert db_link.quantity == 2

    async def test_add_card_to_deck_creates_relationship(
        self, initialize_database, deck_factory, card_factory
    ):
        """Verify that a new card link is created when adding a card to a deck."""
        # Arrange
        deck = await deck_factory({"name": "Test Deck"})
        card = await card_factory({"name": "Test Card"})
        card_data = DeckCardCreate(card_id=card.id, quantity=2)

        # Act
        await crud.add_card_to_deck(deck.id, card_data)

        # Assert (1): Check the relationship from the Deck and Card's perspective
        db_deck = await DeckModel.get(id=deck.id).prefetch_related("deck_cards__card")
        db_card = await CardModel.get(id=card.id).prefetch_related("deck_cards__deck")
        assert len(db_deck.deck_cards) == 1
        assert db_deck.deck_cards[0].card == db_card

        assert len(db_card.deck_cards) == 1
        assert db_card.deck_cards[0].deck == db_deck

    async def test_add_existing_card_to_deck_increases_quantity(
        self, initialize_database, deck_factory, card_factory
    ):
        """Verify that adding an existing card to a deck increases its quantity."""
        # Arrange
        deck = await deck_factory({"name": "Test Deck"})
        card = await card_factory({"name": "Test Card"})
        await DeckCardModel.create(deck=deck, card=card, quantity=1)
        assert await DeckCardModel.all().count() == 1

        card_data = DeckCardCreate(card_id=card.id, quantity=3)

        # Act
        result = await crud.add_card_to_deck(deck.id, card_data)

        # Assert (1): Check the returned Pydantic object
        assert isinstance(result, DeckCardResponseWithCard)
        assert result.quantity == 4  # 1 (initial) + 3 (added)

        # Assert (2): Check the DeckCard table directly
        assert await DeckCardModel.all().count() == 1  # No new link created
        db_link = await DeckCardModel.get(deck_id=deck.id, card_id=card.id)
        assert db_link.quantity == 4

        # Assert (3): Check the relationship from the Deck's perspective
        db_deck = await DeckModel.get(id=deck.id).prefetch_related("deck_cards")
        assert len(db_deck.deck_cards) == 1
        assert db_deck.deck_cards[0].quantity == 4

    async def test_get_cards_for_deck(
        self, initialize_database, deck_factory, card_factory
    ):
        """Verify that all cards for a specific deck are retrieved."""
        # Arrange
        deck = await deck_factory({"name": "Test Deck"})
        card1 = await card_factory({"name": "Card 1"})
        card2 = await card_factory({"name": "Card 2"})
        await DeckCardModel.create(deck=deck, card=card1, quantity=1)
        await DeckCardModel.create(deck=deck, card=card2, quantity=4)

        # Act
        results = await crud.get_cards_for_deck(deck.id)

        # Assert
        assert isinstance(results, list)
        assert len(results) == 2
        assert all(isinstance(r, DeckCardResponseWithCard) for r in results)
        assert {r.card.name for r in results} == {"Card 1", "Card 2"}

    async def test_get_cards_for_empty_deck(self, initialize_database, deck_factory):
        """Verify that getting cards for an empty deck returns an empty list."""
        # Arrange
        deck = await deck_factory({"name": "Empty Deck"})

        # Act
        results = await crud.get_cards_for_deck(deck.id)

        # Assert
        assert isinstance(results, list)
        assert len(results) == 0

    async def test_update_card_quantity_in_deck(
        self, initialize_database, deck_factory, card_factory
    ):
        """Verify that the quantity of a card in a deck can be updated."""
        # Arrange
        deck = await deck_factory({"name": "Test Deck"})
        card = await card_factory({"name": "Test Card"})
        link = await DeckCardModel.create(deck=deck, card=card, quantity=1)
        update_data = DeckCardUpdate(quantity=5)

        # Act
        result = await crud.update_card_quantity_in_deck(link.id, update_data)

        # Assert (1): Check returned Pydantic object
        assert isinstance(result, DeckCardResponseWithCard)
        assert result.id == link.id
        assert result.quantity == 5

        # Assert (2): Check the DeckCard table directly
        db_link = await DeckCardModel.get(id=link.id)
        assert db_link.quantity == 5

    async def test_update_quantity_card_not_found(self, initialize_database):
        """Verify that updating a non-existent deck-card link returns None."""
        # Arrange
        update_data = DeckCardUpdate(quantity=5)
        # Act
        result = await crud.update_card_quantity_in_deck(999, update_data)
        # Assert
        assert result is None

    async def test_remove_card_from_deck(
        self, initialize_database, deck_factory, card_factory
    ):
        """Verify that a card can be removed from a deck."""
        # Arrange
        deck = await deck_factory({"name": "Test Deck"})
        card = await card_factory({"name": "Test Card"})
        link = await DeckCardModel.create(deck=deck, card=card, quantity=1)
        assert await DeckCardModel.all().count() == 1

        # Act
        result = await crud.remove_card_from_deck(link.id)

        # Assert (1): Check return value and that the link is gone from its table
        assert result is True
        assert await DeckCardModel.all().count() == 0
        assert await DeckCardModel.get_or_none(id=link.id) is None

        # Assert (2): Check the relationship from the Deck's perspective is empty
        db_deck = await DeckModel.get(id=deck.id).prefetch_related("deck_cards")
        assert len(db_deck.deck_cards) == 0

        # Assert (3): Check the relationship from the Card's perspective is empty
        db_card = await CardModel.get(id=card.id).prefetch_related("deck_cards")
        assert len(db_card.deck_cards) == 0

    async def test_remove_card_from_deck_not_found(self, initialize_database):
        """Verify that removing a non-existent deck-card link returns False."""
        # Act
        result = await crud.remove_card_from_deck(999)

        # Assert
        assert result is False
