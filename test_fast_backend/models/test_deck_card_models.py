import pytest
from tortoise.exceptions import DoesNotExist, IntegrityError

from fast_backend.app.models.deck_cards import DeckCard
from fast_backend.app.models.decks import Deck
from fast_backend.app.models.cards import Card

# The conftest.py provides the `initialize_database` fixture (autouse)
# and the necessary factories: `deck_factory`, `card_factory`, `deck_card_factory`.


@pytest.mark.skip
@pytest.mark.asyncio
@pytest.mark.usefixtures("initialize_database")
class TestDeckCardModel:
    """
    Test suite for the DeckCard model, which links Decks and Cards.
    """

    CARD_DATA = [{"name": f"Card {i}", "text": f"Text {i}"} for i in range(1, 6)]
    DECK_DATA = [
        {"name": f"Deck {i}", "description": f"Description for Deck {i}"}
        for i in range(1, 4)
    ]

    @pytest.mark.parametrize("card_data", CARD_DATA)
    @pytest.mark.parametrize("deck_data", DECK_DATA)
    async def test_create_deck_card_link_object(
        self,
        initialize_database,
        deck_factory,
        card_factory,
        deck_card_factory,
        card_data,
        deck_data,
    ):
        """Verify that a DeckCard object can be created in the database."""
        # Arrange
        card = await card_factory(card_data)
        deck = await deck_factory(deck_data)
        test_quantity = 2

        # Act
        deck_card_link = await deck_card_factory(
            deck=deck, card=card, quantity=test_quantity
        )

        # Assert (1): Check the returned DeckCard object itself.
        assert deck_card_link.id is not None
        assert deck_card_link.quantity == test_quantity
        assert deck_card_link.deck_id == deck.id
        assert deck_card_link.card_id == card.id

        # Assert (2): Verify the DeckCard object exists and is correct in the database.
        db_link = await DeckCard.get(id=deck_card_link.id)
        assert db_link is not None
        assert db_link.deck_id == deck.id
        assert db_link.card_id == card.id
        assert db_link.quantity == test_quantity

    @pytest.mark.parametrize("card_data", CARD_DATA)
    @pytest.mark.parametrize("deck_data", DECK_DATA)
    async def test_deck_sees_linked_card_after_creation(
        self,
        initialize_database,
        deck_factory,
        card_factory,
        deck_card_factory,
        card_data,
        deck_data,
    ):
        """Verify that a Deck's relationship field contains the linked card."""
        # Arrange
        card = await card_factory(card_data)
        deck = await deck_factory(deck_data)
        test_quantity = 3

        # Act
        await deck_card_factory(deck=deck, card=card, quantity=test_quantity)

        # Assert
        db_deck = await Deck.get(id=deck.id).prefetch_related("deck_cards__card")
        assert len(db_deck.deck_cards) == 1

        linked_card_info = db_deck.deck_cards[0]
        assert linked_card_info.quantity == test_quantity
        assert linked_card_info.card.id == card.id
        assert linked_card_info.card.name == card.name

    @pytest.mark.parametrize("card_data", CARD_DATA)
    @pytest.mark.parametrize("deck_data", DECK_DATA)
    async def test_card_sees_linked_deck_after_creation(
        self,
        initialize_database,
        deck_factory,
        card_factory,
        deck_card_factory,
        card_data,
        deck_data,
    ):
        """Verify that a Card's relationship field contains the linked deck."""
        # Arrange
        card = await card_factory(card_data)
        deck = await deck_factory(deck_data)
        test_quantity = 4

        # Act
        await deck_card_factory(deck=deck, card=card, quantity=test_quantity)

        # Assert
        db_card = await Card.get(id=card.id).prefetch_related("deck_cards__deck")
        assert len(db_card.deck_cards) == 1

        linked_deck_info = db_card.deck_cards[0]
        assert linked_deck_info.quantity == test_quantity
        assert linked_deck_info.deck.id == deck.id
        assert linked_deck_info.deck.name == deck.name

    @pytest.mark.parametrize("deck_data", DECK_DATA)
    @pytest.mark.parametrize("card_data", CARD_DATA)
    async def test_read_deck_card_link(
        self,
        initialize_database,
        deck_factory,
        card_factory,
        deck_card_factory,
        deck_data,
        card_data,
    ):
        """Verify that a DeckCard link can be read from the database."""
        # Arrange: Create a card, a deck, and a link using factories.
        card = await card_factory(card_data)
        deck = await deck_factory(deck_data)
        created_link = await deck_card_factory(deck=deck, card=card, quantity=18)

        # Act: Fetch the link by its ID.
        read_link = await DeckCard.get(id=created_link.id)

        # Assert: Check that the fetched data is correct.
        assert read_link.id == created_link.id
        assert read_link.deck_id == deck.id
        assert read_link.card_id == card.id
        assert read_link.quantity == 18

    @pytest.mark.parametrize("deck_data", DECK_DATA)
    @pytest.mark.parametrize("card_data", CARD_DATA)
    async def test_update_deck_card_quantity(
        self,
        initialize_database,
        deck_factory,
        card_factory,
        deck_card_factory,
        deck_data,
        card_data,
    ):
        """Verify that a DeckCard link's quantity can be updated."""
        # Arrange: Create a card, a deck, and a link with an initial quantity.
        card = await card_factory(card_data)
        deck = await deck_factory(deck_data)
        link = await deck_card_factory(deck=deck, card=card, quantity=1)

        # Act: Update the quantity and save the change.
        link.quantity = 4  # This is not a legal deck, just a test!
        await link.save()

        # Assert: Fetch the link again and check if the update was persisted.
        updated_link = await DeckCard.get(id=link.id)
        assert updated_link.quantity == 4

    @pytest.mark.parametrize("deck_data", DECK_DATA)
    @pytest.mark.parametrize("card_data", CARD_DATA)
    async def test_deck_sees_updated_quantity(
        self,
        initialize_database,
        deck_factory,
        card_factory,
        deck_card_factory,
        deck_data,
        card_data,
    ):
        """Verify a Deck sees the updated quantity after its linked card is changed."""
        # Arrange
        card = await card_factory(card_data)
        deck = await deck_factory(deck_data)
        link = await deck_card_factory(deck=deck, card=card, quantity=1)
        new_quantity = 5

        # Act
        link.quantity = new_quantity
        await link.save()

        # Assert
        db_deck = await Deck.get(id=deck.id).prefetch_related("deck_cards")
        assert len(db_deck.deck_cards) == 1
        assert db_deck.deck_cards[0].quantity == new_quantity

    @pytest.mark.parametrize("deck_data", DECK_DATA)
    @pytest.mark.parametrize("card_data", CARD_DATA)
    async def test_card_sees_updated_quantity(
        self,
        initialize_database,
        deck_factory,
        card_factory,
        deck_card_factory,
        deck_data,
        card_data,
    ):
        """Verify a Card sees the updated quantity after its linked deck is changed."""
        # Arrange
        card = await card_factory(card_data)
        deck = await deck_factory(deck_data)
        link = await deck_card_factory(deck=deck, card=card, quantity=1)
        new_quantity = 6

        # Act
        link.quantity = new_quantity
        await link.save()

        # Assert
        db_card = await Card.get(id=card.id).prefetch_related("deck_cards")
        assert len(db_card.deck_cards) == 1
        assert db_card.deck_cards[0].quantity == new_quantity

    @pytest.mark.parametrize("deck_data", DECK_DATA)
    @pytest.mark.parametrize("card_data", CARD_DATA)
    async def test_deck_card_uniqueness(
        self,
        initialize_database,
        deck_factory,
        card_factory,
        deck_card_factory,
        card_data,
        deck_data,
    ):
        """Verify that the same card cannot be linked to the same deck twice."""
        # Arrange: Create a card and a deck.
        card = await card_factory(card_data)
        deck = await deck_factory(deck_data)

        # Create the first link successfully.
        await deck_card_factory(deck=deck, card=card, quantity=1)

        # Act & Assert: Attempting to create the exact same link again
        # should raise an IntegrityError due to the unique_together constraint.
        with pytest.raises(IntegrityError):
            await deck_card_factory(deck=deck, card=card, quantity=3)

    @pytest.mark.parametrize("deck_data", DECK_DATA)
    @pytest.mark.parametrize("card_data", CARD_DATA)
    async def test_delete_deck_card_link(
        self,
        initialize_database,
        deck_factory,
        card_factory,
        deck_card_factory,
        deck_data,
        card_data,
    ):
        """Verify deleting a DeckCard link removes it and updates relationships."""
        # Arrange
        card = await card_factory(card_data)
        deck = await deck_factory(deck_data)
        link_to_delete = await deck_card_factory(deck=deck, card=card)
        assert await DeckCard.all().count() == 1

        # Act
        await link_to_delete.delete()

        # Assert (1): Confirm the DeckCard record is gone from the database.
        assert await DeckCard.all().count() == 0
        with pytest.raises(DoesNotExist):
            await DeckCard.get(id=link_to_delete.id)

        # Assert (2): Verify the relationship is gone from the Deck's perspective.
        db_deck = await Deck.get(id=deck.id).prefetch_related("deck_cards")
        assert len(db_deck.deck_cards) == 0

        # Assert (3): Verify the relationship is gone from the Card's perspective.
        db_card = await Card.get(id=card.id).prefetch_related("deck_cards")
        assert len(db_card.deck_cards) == 0

    async def test_deleting_deck_cascades_to_deck_card(
        self, initialize_database, deck_factory, card_factory, deck_card_factory
    ):
        """Verify that deleting a Deck also deletes its DeckCard links."""
        # Arrange
        deck = await deck_factory({"name": "Deck to be Deleted"})
        card = await card_factory({"name": "Card in Deck"})
        await deck_card_factory(deck=deck, card=card)
        assert await DeckCard.filter(deck_id=deck.id).count() == 1
        assert await DeckCard.filter(card_id=card.id).count() == 1

        # Act
        await deck.delete()

        # Assert
        assert await DeckCard.filter(deck_id=deck.id).count() == 0
        db_card = await Card.get(id=card.id).prefetch_related("deck_cards__deck")
        assert len(db_card.deck_cards) == 0

    async def test_deleting_card_cascades_to_deck_card(
        self, initialize_database, deck_factory, card_factory, deck_card_factory
    ):
        """Verify that deleting a Card also deletes its DeckCard links."""
        # Arrange
        deck = await deck_factory({"name": "Deck with card"})
        card = await card_factory({"name": "Card to be Deleted"})
        await deck_card_factory(deck=deck, card=card)
        assert await DeckCard.filter(deck_id=deck.id).count() == 1
        assert await DeckCard.filter(card_id=card.id).count() == 1

        # Act
        await card.delete()

        # Assert
        assert await DeckCard.filter(card_id=card.id).count() == 0
        db_deck = await Deck.get(id=deck.id).prefetch_related("deck_cards")
        assert len(db_deck.deck_cards) == 0

    async def test_deck_can_see_its_cards(
        self, initialize_database, deck_factory, card_factory, deck_card_factory
    ):
        """Verify that a Deck can access its linked Cards through the relationship."""
        # Arrange: Create a deck, a card, and link them.
        deck = await deck_factory({"name": "Parent Deck"})
        card = await card_factory({"name": "Child Card"})
        await deck_card_factory(deck=deck, card=card, quantity=4)

        # Act: Fetch the deck and prefetch its related cards.
        db_deck = await Deck.get(id=deck.id).prefetch_related("deck_cards__card")

        # Assert: Check that the relationship is correctly established.
        assert db_deck.deck_cards is not None
