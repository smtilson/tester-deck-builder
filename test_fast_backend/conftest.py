"""
Shared test configuration and fixtures for the test suite.
"""

import pytest
import pytest_asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from tortoise import Tortoise
from typing import Callable, Awaitable, Any, AsyncGenerator
from uuid import uuid4
from fastapi.testclient import TestClient
import random


from fast_backend.app.models.cards import Card
from fast_backend.app.models.decks import Deck
from fast_backend.app.models.deck_cards import DeckCard
from fast_backend.app.models.users import User
from fast_backend.app.db.users_db import get_user_db
from fast_backend.app.auth.manager import UserManager, get_user_manager
from fast_backend.app.auth.backend import auth_backend
from fast_backend.app.main import app


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


@pytest_asyncio.fixture  # (scope="function", autouse=True)
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
        return_value=AsyncMock(return_value=manager_instance),
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


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture
def mock_db_data():
    """
    Provides mock ORM objects for users, cards, decks, and deck_cards.
    These objects mimic the structure of your Tortoise ORM models.
    """
    # Mock Cards
    mock_cards = []
    for card in SAMPLE_CARDS:
        card["id"] = random.randint(1, 1000)
        mock_cards.append(MagicMock(**card))
    # Mock Decks
    mock_decks = []
    for deck in SAMPLE_DECKS:
        deck["id"] = random.randint(1, 1000)
        mock_decks.append(MagicMock(**deck))
    # Mock deck_cards
    mock_deck_cards = []
    for deck in mock_decks:
        for _ in range(random.randint(len(mock_cards))):
            deck_card = {
                "id": random.randint(1, 1000),
                "deck_id": deck.id,
                "card_id": random.choice(mock_cards).id,
                "quantity": random.randint(1, 4),
            }
            mock_deck_cards.append(MagicMock(**deck_card))

    return {
        "cards": mock_cards,
        "decks": mock_decks,
        "deck_cards": mock_deck_cards,
    }


@pytest.fixture
async def override_app_dependencies():
    """
    Patches global app dependencies like get_user_db, get_user_manager,
    auth_backend, and Tortoise lifecycle methods to return simple AsyncMocks.
    This ensures the FastAPI app itself uses mocked dependencies and no real DB connection.
    """
    # Create simple mocks for the dependencies
    mock_user_db_adapter = AsyncMock()
    mock_user_manager_instance = AsyncMock()
    mock_user_manager_instance.on_after_register.return_value = (
        None  # Prevent actual email sending
    )
    mock_user_manager_instance.authenticate.return_value = MagicMock(
        id=uuid4(), email="auth@example.com"
    )

    mock_auth_backend_strategy = MagicMock(
        read_token=AsyncMock(return_value={"sub": str(uuid4())}),
        write_token=AsyncMock(return_value={"access_token": "mock_jwt_token"}),
    )

    # Patch the dependency functions in the modules where they are defined/imported
    with patch(
        "fast_backend.app.db.users_db.get_user_db", return_value=mock_user_db_adapter
    ):
        with patch(
            "fast_backend.app.auth.manager.get_user_manager",
            return_value=AsyncMock(return_value=mock_user_manager_instance),
        ):
            with patch(
                "fast_backend.app.auth.backend.auth_backend.get_strategy",
                return_value=mock_auth_backend_strategy,
            ):
                # 🐛 Crucial patches for Tortoise lifecycle methods
                with patch.object(
                    Tortoise, "init", new_callable=AsyncMock
                ) as mock_tortoise_init:
                    with patch.object(
                        Tortoise, "close_connections", new_callable=AsyncMock
                    ) as mock_tortoise_close:
                        yield  # Allow the test to run

    # Cleanup is handled by patch's context manager


# --- 3. Patching ORM Models (Autouse to apply to all tests) ---
@pytest.fixture
def mock_orm_models(mock_db_data):
    """
    Patches the .all() and .get() methods of Tortoise ORM models
    to return mock data, preventing real database calls.
    """
    # Patch Card.all() and .get()
    with patch.object(Card, "all", new_callable=AsyncMock) as mock_card_all:
        mock_card_all.return_value = mock_db_data["cards"]
        with patch.object(Card, "get", new_callable=AsyncMock) as mock_card_get:
            mock_card_get.side_effect = lambda **kwargs: next(
                (
                    c
                    for c in mock_db_data["cards"]
                    if all(getattr(c, k) == v for k, v in kwargs.items())
                ),
                None,
            )
            # Patch Deck.all() and .get()
            with patch.object(Deck, "all", new_callable=AsyncMock) as mock_deck_all:
                mock_deck_all.return_value = mock_db_data["decks"]
                with patch.object(Deck, "get", new_callable=AsyncMock) as mock_deck_get:
                    mock_deck_get.side_effect = lambda **kwargs: next(
                        (
                            d
                            for d in mock_db_data["decks"]
                            if all(getattr(d, k) == v for k, v in kwargs.items())
                        ),
                        None,
                    )
                    # Patch DeckCard.all() and .get()
                    with patch.object(
                        DeckCard, "all", new_callable=AsyncMock
                    ) as mock_deck_card_all:
                        mock_deck_card_all.return_value = mock_db_data["deck_cards"]
                        with patch.object(
                            DeckCard, "get", new_callable=AsyncMock
                        ) as mock_deck_card_get:
                            mock_deck_card_get.side_effect = lambda **kwargs: next(
                                (
                                    dc
                                    for dc in mock_db_data["deck_cards"]
                                    if all(
                                        getattr(dc, k) == v for k, v in kwargs.items()
                                    )
                                ),
                                None,
                            )
                            yield  # Allow tests to run within this patched context


