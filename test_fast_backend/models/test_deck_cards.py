import pytest
from tortoise.exceptions import DoesNotExist, IntegrityError

from fast_backend.app.models.deck_cards import DeckCard
from fast_backend.app.models.decks import Deck
from fast_backend.app.models.cards import Card

# The conftest.py provides the `initialize_database` fixture (autouse)
# and the necessary factories: `deck_factory`, `card_factory`.


@pytest.mark.asyncio
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
    async def test_create_deck_card_link(
        self, deck_factory, card_factory, deck_card_factory, card_data, deck_data
    ):
        """Verify that a link between a Deck and a Card can be created."""
        # Arrange: Create the parent objects.
        card = await card_factory(card_data)
        deck = await deck_factory(deck_data)

        # Act: Create the link between them.
        deck_card_link = await DeckCard.create(deck=deck, card=card, quantity=2)

        # Assert: Check that the link was created correctly.
        assert deck_card_link.id is not None
        assert deck_card_link.quantity == 2

        # Verify the foreign keys are set correctly.
        assert deck_card_link.deck_id == deck.id
        assert deck_card_link.card_id == card.id

        # Assert: Verify it exists in the database by fetching it again.
        db_link = await DeckCard.get(id=deck_card_link.id).prefetch_related(
            "deck", "card"
        )
        assert db_link is not None
        assert db_link.deck.name == deck.name
        assert db_link.card.name == card.name

    @pytest.mark.parametrize("deck_data", DECK_DATA)
    @pytest.mark.parametrize("card_data", CARD_DATA)
    async def test_read_deck_card_link(
        self, deck_factory, card_factory, deck_card_factory, deck_data, card_data
    ):
        """Verify that a DeckCard link can be read from the database."""
        # Arrange: Create a card, a deck, and a link.
        card = await card_factory(card_data)
        deck = await deck_factory(deck_data)
        created_link = await DeckCard.create(deck=deck, card=card, quantity=18)

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
        self, deck_factory, card_factory, deck_card_factory, deck_data, card_data
    ):
        """Verify that a DeckCard link's quantity can be updated."""
        # Arrange: Create a card, a deck, and a link with an initial quantity.
        card = await card_factory(card_data)
        deck = await deck_factory(deck_data)
        link = await DeckCard.create(deck=deck, card=card, quantity=1)

        # Act: Update the quantity and save the change.
        link.quantity = 4  # This is not a legal deck, just a test!
        await link.save()

        # Assert: Fetch the link again and check if the update was persisted.
        updated_link = await DeckCard.get(id=link.id)
        assert updated_link.quantity == 4

    @pytest.mark.parametrize("deck_data", DECK_DATA)
    @pytest.mark.parametrize("card_data", CARD_DATA)
    async def test_delete_deck_card_link(
        self, deck_factory, card_factory, deck_card_factory, deck_data, card_data
    ):
        """Verify that a DeckCard link can be deleted."""
        # Arrange: Create a card, a deck, and a link to be deleted.
        card = await card_factory(card_data)
        deck = await deck_factory(deck_data)
        link_to_delete = await DeckCard.create(deck=deck, card=card)
        link_id = link_to_delete.id

        # Confirm it's in the database before deletion.
        assert await DeckCard.all().count() == 1

        # Act: Delete the link.
        await link_to_delete.delete()

        # Assert: Confirm it's no longer in the database.
        assert await DeckCard.all().count() == 0
        with pytest.raises(DoesNotExist):
            await DeckCard.get(id=link_id)

    async def test_deck_card_uniqueness(self, deck_factory, card_factory):
        """Verify that the same card cannot be linked to the same deck twice."""
        # Arrange: Create a card and a deck.
        card = await card_factory(name="Brainstorm")
        deck = await deck_factory(name="Legacy Miracles")

        # Create the first link successfully.
        await DeckCard.create(deck=deck, card=card, quantity=1)

        # Act & Assert: Attempting to create the exact same link again
        # should raise an IntegrityError due to the unique_together constraint.
        with pytest.raises(IntegrityError):
            await DeckCard.create(deck=deck, card=card, quantity=3)
