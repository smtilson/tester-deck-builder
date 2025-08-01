"""
Shared test configuration and fixtures for the test suite.
"""

import pytest
import pytest_asyncio
from tortoise import Tortoise
from typing import Callable, Awaitable, Any, AsyncGenerator
from uuid import UUID

from fast_backend.app.models.cards import Card
from fast_backend.app.models.decks import Deck
from fast_backend.app.models.deck_cards import DeckCard
from fast_backend.app.models.users import User
from fast_backend.app.db.users_db import get_user_db
from fast_backend.app.services.user_services.manager import UserManager


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
async def user_manager(initialize_database) -> AsyncGenerator[UserManager, None]:
    """Provide a resolved UserManager instance for tests."""
    user_db_generator = get_user_db()
    user_db_instance = await anext(user_db_generator)

    try:
        manager_instance = UserManager(user_db_instance)
        yield manager_instance
    finally:
        await user_db_generator.aclose()


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
