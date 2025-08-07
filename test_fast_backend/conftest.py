"""
Shared test configuration and fixtures for the test suite.
"""

import pytest
import pytest_asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from tortoise import Tortoise
from typing import Callable, Awaitable, Any, AsyncGenerator
from uuid import UUID

from fast_backend.app.models.cards import Card
from fast_backend.app.models.decks import Deck
from fast_backend.app.models.deck_cards import DeckCard
from fast_backend.app.models.users import User
from fast_backend.app.db.users_db import get_user_db
from fast_backend.app.auth.manager import UserManager, get_user_manager



# Test Data Constants
SAMPLE_CARDS = [
    {"name": "Lightning Bolt", "text": "Deal 3 damage to any target."},
    {"name": "Counterspell", "text": "Counter target spell."},
    {"name": "Giant Growth", "text": "+3/+3 until end of turn."},
]

SAMPLE_DECKS = [
    {"name": "Red Aggro", "description": "Fast aggressive deck"},
    {"name": "Blue Control", "description": "Control the game"},
    {"name": "Green Ramp", "description": "Big creatures"},
]

SAMPLE_USERS = [
    {
        "username": "testuser1",
        "email": "test1@example.com",
        "password": "Password123!",
        "name": "Test User 1",
    },
    {
        "username": "testuser2",
        "email": "test2@example.com",
        "password": "Password456!",
        "name": "Test User 2",
    },
]



@pytest_asyncio.fixture(scope="function", autouse=True)
async def initialize_database():
    """Initialize clean in-memory database for each test."""
    DATABASE_URL = "sqlite://:memory:"
    await Tortoise.init(
        db_url=DATABASE_URL, modules={"models": ["fast_backend.app.models"]}
    )
    await Tortoise.generate_schemas()

    yield

    await Tortoise.close_connections()



@pytest_asyncio.fixture
def mock_on_after_register_spy():
    """
    Creates a spy function that calls the mocked nested methods.
    This replaces the real on_after_register method in the UserManager.
    """
    # Create the mocks for the functions inside on_after_register
    mock_render_template = MagicMock(return_value="Welcome email HTML")
    mock_queue_enqueue = AsyncMock(return_value=None)
    
    # Create a MagicMock to act as the spy
    on_after_register_spy = AsyncMock()

    # Define the side_effect for the spy. When the spy is called,
    # this function will run, calling the nested mocks.
    async def spy_implementation(user, request=None):
        print("spy function called")
        name = user.name
        subject = f"Welcome to {name}!" if name else "Welcome!"
        await mock_queue_enqueue.enqueue(
            "send_email_task",
            recipient=(user.email, None),
            subject=subject,
            html=mock_render_template("welcome.html", context={"user": user}),
        )

    on_after_register_spy.side_effect = spy_implementation
    
    # Attach the nested mocks to the spy so we can inspect them later
    on_after_register_spy.render_email_template = mock_render_template
    on_after_register_spy.queue_enqueue = mock_queue_enqueue

    return on_after_register_spy



@pytest_asyncio.fixture
async def user_manager(
    initialize_database,
    mock_on_after_register_spy,
) -> AsyncGenerator[UserManager, None]:
    """
    Provides a resolved UserManager instance with the on_after_register
    method replaced with our spy function by patching the dependency function.
    """
    # Create an instance of UserManager with the mocked method.
    user_db_generator = get_user_db()
    user_db_instance = await anext(user_db_generator)

    manager_instance = UserManager(user_db_instance)
    manager_instance.on_after_register = mock_on_after_register_spy

    # Patch the dependency function to return our mocked instance
    with patch(
        "fast_backend.app.auth.manager.get_user_manager",
        return_value=AsyncMock(return_value=manager_instance)
    ):
        yield manager_instance
        await user_db_generator.aclose()


@pytest.fixture(scope="function")
def card_factory() -> Callable[[dict], Awaitable[Card]]:
    """Factory for creating test cards."""

    async def _create_card(card_data: dict = None) -> Card:
        if card_data is None:
            card_data = SAMPLE_CARDS[0]
        return await Card.create(**card_data)

    return _create_card


@pytest.fixture(scope="function")
def deck_factory() -> Callable[[dict], Awaitable[Deck]]:
    """Factory for creating test decks."""

    async def _create_deck(deck_data: dict = None) -> Deck:
        if deck_data is None:
            deck_data = SAMPLE_DECKS[0].copy()

        # Ensure deck has an owner_id
        if "owner_id" not in deck_data:
            deck_data["owner_id"] = 1

        return await Deck.create(**deck_data)

    return _create_deck


@pytest.fixture(scope="function")
def deck_card_factory() -> Callable[[Deck, Card, int], Awaitable[DeckCard]]:
    """Factory for creating deck-card relationships."""

    async def _create_deck_card(deck: Deck, card: Card, quantity: int = 1) -> DeckCard:
        return await DeckCard.create(deck=deck, card=card, quantity=quantity)

    return _create_deck_card


@pytest.fixture(scope="function")
def user_factory() -> Callable[[dict], Awaitable[User]]:
    """Factory for creating test users."""

    async def _create_user(user_data: dict = None) -> User:
        if user_data is None:
            user_data = SAMPLE_USERS[0]
        return await User.create(**user_data)

    return _create_user
