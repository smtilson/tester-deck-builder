# conftest.py
import uuid
import pytest
import pytest_asyncio
from tortoise import Tortoise
from httpx import AsyncClient
from typing import Dict, List, Any
from fast_backend.app.db.config_db import MODEL_PATHS

TEST_DB_URL = "sqlite://:memory:"
TEST_MODULES = {"models": ["fast_backend.app.models"]}


@pytest_asyncio.fixture(scope="function")
async def init_db():
    """
    Create the in-memory test DB once for the whole test session.
    Drop it after all tests are done.
    """
    TEST_DB_URL = "sqlite://:memory:"
    await Tortoise.init(
        db_url=TEST_DB_URL,
        modules=TEST_MODULES
    )
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()

# I think this can be deleted
@pytest.fixture
async def db():
    """
    Empty the database between tests to keep them isolated.
    """
    for model in Tortoise.apps["models"].values():
        await model.all().delete()
    yield


@pytest.fixture
def user_test_data() -> List[Dict[str, Any]]:
    """Create test user data for database creation."""
    return [
        {
            "id": uuid.uuid4(),
            "username": "testuser1",
            "email": "test1@example.com",
            "password": "password123",
            "name": "Test User One",
            "is_active": True,
            "is_superuser": False,
            "is_verified": True,
            "is_admin": False,
        },
        {
            "id": uuid.uuid4(),
            "username": "admin_user",
            "email": "admin@example.com",
            "password": "adminpass123",
            "name": "Admin User",
            "is_active": True,
            "is_superuser": True,
            "is_verified": True,
            "is_admin": True,
        },
        {
            "id": uuid.uuid4(),
            "username": "inactive_user",
            "email": "inactive@example.com",
            "password": "password123",
            "name": "Inactive User",
            "is_active": False,
            "is_superuser": False,
            "is_verified": False,
            "is_admin": False,
        },
    ]


@pytest.fixture
def card_test_data() -> List[Dict[str, Any]]:
    """Create test card data for database creation."""
    return [
        {
            "id": 1,
            "name": "Lightning Bolt",
            "text": "Lightning Bolt deals 3 damage to any target.",
        },
        {
            "id": 2,
            "name": "Giant Growth",
            "text": "Target creature gets +3/+3 until end of turn.",
        },
        {
            "id": 3,
            "name": "Counterspell",
            "text": "Counter target spell.",
        },
        {
            "id": 4,
            "name": "Basic Land",
            "text": None,
        },
    ]


@pytest.fixture
def deck_test_data(user_test_data) -> List[Dict[str, Any]]:
    """Create test deck data for database creation."""
    # Use the first user as the default owner
    default_owner_id = user_test_data[0]["id"]
    admin_owner_id = user_test_data[1]["id"]
    
    return [
        {
            "id": 1,
            "name": "Red Burn Deck",
            "description": "A fast aggressive red deck focused on dealing damage quickly.",
            "is_valid": True,
            "owner_id": default_owner_id,
        },
        {
            "id": 2,
            "name": "Blue Control",
            "description": "A control deck that counters spells and draws cards.",
            "is_valid": True,
            "owner_id": admin_owner_id,
        },
        {
            "id": 3,
            "name": "Work in Progress",
            "description": "An incomplete deck still being built.",
            "is_valid": False,
            "owner_id": default_owner_id,
        },
    ]


@pytest.fixture
def deck_card_test_data(card_test_data, deck_test_data) -> List[Dict[str, Any]]:
    """Create test deck_card data for database creation."""
    # Extract deck and card IDs from the test data
    deck_ids = [deck["id"] for deck in deck_test_data]
    card_ids = [card["id"] for card in card_test_data]
    
    return [
        {
            "id": 1,
            "deck_id": deck_ids[0],  # Red Burn Deck
            "card_id": card_ids[0],  # Lightning Bolt
            "quantity": 4,
        },
        {
            "id": 2,
            "deck_id": deck_ids[0],  # Red Burn Deck
            "card_id": card_ids[3],  # Basic Land
            "quantity": 20,
        },
        {
            "id": 3,
            "deck_id": deck_ids[1],  # Blue Control
            "card_id": card_ids[2],  # Counterspell
            "quantity": 4,
        },
        {
            "id": 4,
            "deck_id": deck_ids[1],  # Blue Control
            "card_id": card_ids[3],  # Basic Land
            "quantity": 24,
        },
        {
            "id": 5,
            "deck_id": deck_ids[2],  # Work in Progress
            "card_id": card_ids[1],  # Giant Growth
            "quantity": 2,
        },
    ]


@pytest.fixture
def all_test_data(user_test_data, card_test_data, deck_test_data, deck_card_test_data):
    """Composite fixture that provides all test data."""
    class TestData:
        def __init__(self):
            self.user_data = user_test_data
            self.card_data = card_test_data
            self.deck_data = deck_test_data
            self.deck_card_data = deck_card_test_data
        
        def get_user_by_username(self, username: str) -> Dict[str, Any]:
            """Get user data by username."""
            for user in self.user_data:
                if user["username"] == username:
                    return user
            raise ValueError(f"User with username '{username}' not found")
        
        def get_card_by_name(self, name: str) -> Dict[str, Any]:
            """Get card data by name."""
            for card in self.card_data:
                if card["name"] == name:
                    return card
            raise ValueError(f"Card with name '{name}' not found")
        
        def get_deck_by_name(self, name: str) -> Dict[str, Any]:
            """Get deck data by name."""
            for deck in self.deck_data:
                if deck["name"] == name:
                    return deck
            raise ValueError(f"Deck with name '{name}' not found")
        
        def get_deck_cards_by_deck_id(self, deck_id: int) -> List[Dict[str, Any]]:
            """Get all deck_card data for a specific deck."""
            return [dc for dc in self.deck_card_data if dc["deck_id"] == deck_id]
    
    return TestData()


@pytest.fixture
async def client():
    """
    HTTP client for endpoint tests (works later when testing FastAPI routes).
    """
    # async with AsyncClient(app=app, base_url="http://test") as ac:
    #     yield ac
    pass  # TODO: Import and use the FastAPI app when needed
