import pytest
import pytest_asyncio  # <--- IMPORT THIS
from tortoise import Tortoise
from typing import Callable, Awaitable, Any
from fast_backend.app.models.cards import Card
from fast_backend.app.models.decks import Deck
from fast_backend.app.models.deck_cards import DeckCard



# THIS IS THE CRITICAL FIX: Use the special decorator for async fixtures.
@pytest_asyncio.fixture(scope="function", autouse=True)
async def initialize_database():
    """
    Initializes an in-memory SQLite database for each test function.
    """
    await Tortoise.init(
        db_url="sqlite://:memory:",
        # This discovers the models in your app
        modules={"models": ["fast_backend.app.models"]}
    )
    # Creates the database tables
    await Tortoise.generate_schemas()

    # 'yield' passes control to the test function
    yield

    # This runs after the test is complete
    await Tortoise.close_connections()
    
# The other factories are synchronous, so they use the standard decorator.
@pytest.fixture(scope="function")
def card_factory() -> Callable[[dict], Awaitable[Card]]:
    """
    Provides factory for creating cards in the database.
    """
    async def _create_card(card_data=dict)-> Card:
        card = await Card.create(**card_data)
        return card
    return _create_card

@pytest.fixture(scope="function")
def deck_factory() -> Callable[[dict], Awaitable[Deck]]:
    """
    Provides factory for creating decks in the database.
    """
    async def _create_deck(deck_data=dict) -> Deck:
        # Ensure the deck data includes an owner_id
        deck_data["owner_id"] = 1
        deck = await Deck.create(**deck_data)
        return deck
    return _create_deck

@pytest.fixture(scope="function")
def deck_card_factory() -> Callable[[dict], Awaitable[DeckCard]]:
    """
    Provides factory for creating deck cards in the database.
    """
    async def _create_deck_card_link(deck: Deck, card: Card, quantity: int=1) -> DeckCard:
        deck_card = await DeckCard.create(deck=deck, card=card, quantity=quantity)
        return deck_card
    return _create_deck_card_link
