import pytest
import uuid
from typing import Any
from datetime import datetime
import random
from beanie.odm.fields import PydanticObjectId


@pytest.fixture
def user_test_data() -> list[dict[str, Any]]:
    """Create test user data for database creation."""
    return [
        {
            "username": "testuser1",
            "email": "test1@example.com",
            "password": "password123",
            "confirm_password":"password123",
        },
        {
            "username": "admin_user",
            "email": "admin@example.com",
            "password": "adminpass123",
            "confirm_password": "adminpass123",
        },
        {
            "username": "inactive_user",
            "email": "inactive@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
    ]


@pytest.fixture
def card_test_data() -> list[dict[str, Any]]:
    """Create test card data for database creation."""
    return [
        {
            "name": "Lightning Bolt",
            "text": "Lightning Bolt deals 3 damage to any target.",
        },
        {
            "name": "Giant Growth",
            "text": "Target creature gets +3/+3 until end of turn.",
        },
        {
            "name": "Counterspell",
            "text": "Counter target spell.",
        },
        {
            "name": "Basic Land",
            "text": "not none",
        },
    ]


@pytest.fixture
def deck_test_data() -> list[dict[str, Any]]:
    """Create test deck data for database creation."""
    # Use the first user as the default owner
    return [
        {
            "name": "Red Burn Deck",
            "description": "A fast aggressive red deck focused on dealing damage quickly.",
        },
        {
            "name": "Blue Control",
            "description": "A control deck that counters spells and draws cards.",
        },
        {
            "name": "Work in Progress",
            "description": "An incomplete deck still being built.",
        },
    ]

'''
@pytest.fixture
def deck_card_test_data(card_test_data, deck_test_data) -> list[dict[str, Any]]:
    """Create test deck_card data for database creation."""
    # Extract deck and card IDs from the test data
    deck_ids = [deck["id"] for deck in deck_test_data]
    card_ids = [card["id"] for card in card_test_data]

    return [
        {
            "deck_id": deck_ids[0],  # Red Burn Deck
            "card_id": card_ids[0],  # Lightning Bolt
            "quantity": 4,
        },
        {
            "deck_id": deck_ids[0],  # Red Burn Deck
            "card_id": card_ids[3],  # Basic Land
            "quantity": 20,
        },
        {
            "deck_id": deck_ids[1],  # Blue Control
            "card_id": card_ids[2],  # Counterspell
            "quantity": 4,
        },
        {
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

'''

@pytest.fixture
def game_test_data() -> list[dict[str, Any]]:
    """Create test game data for database creation based on Game model."""
    return [
        {
            "name": "Magic: The Gathering",
            "version": "1.0.0",
            "description": "A collectible card game created by Richard Garfield.",
            "designer_ids": [],  # Fill with Link[User] objects if needed
            "publisher": "Wizards of the Coast",
            "developer_ids": [],  # Fill with Link[User] objects if needed
            "release_date": datetime(1993, 8, 5),
        },
        {
            "name": "Pokémon TCG",
            "version": "2.1.0",
            "description": "A trading card game based on Pokémon franchise.",
            "designer_ids": [],
            "publisher": "The Pokémon Company",
            "developer_ids": [],
            "release_date": datetime(1996, 10, 20),
        },
        {
            "name": "Yu-Gi-Oh!",
            "version": "3.0.0",
            "description": "A Japanese collectible card game developed by Konami.",
            "designer_ids": [],
            "publisher": "Konami",
            "developer_ids": [],
            "release_date": datetime(1999, 2, 4),
        },
    ]

@pytest.fixture
def all_test_data(user_test_data, card_test_data, deck_test_data, game_test_data):
    """Composite fixture that provides all test data."""

    class TestData:
        def __init__(self, already_picked=None):
            self.user_data = user_test_data
            self.card_data = card_test_data
            #self.deck_card_data = deck_card_test_data
            self.game_data = game_test_data
            self.deck_data = deck_test_data
            # I don't think I need the id business
            #self.default_user_id = deck_test_data[0]["owner_id"]
            if already_picked is None:
                self.already_picked = {"users":set(),"cards":set(),"decks":set(),"deck_cards":set(),"games":set()}
            else:
                self.already_picked = already_picked            
        
        def _get_by_key(self, data_list, key, value) -> dict[str, Any]:
            """Generic method to get an item by key from a list of dicts."""
            for item in data_list:
                if item.get(key, None) == value:
                    return item
            raise ValueError(f"{key.capitalize()} with value '{value}' not found")

        def get_user_by_username(self, username: str) -> dict[str, Any]:
            return self._get_by_key(self.user_data, "username", username)

        def get_card_by_name(self, name: str) -> dict[str, Any]:
            return self._get_by_key(self.card_data, "name", name)

        def get_deck_by_name(self, name: str) -> dict[str, Any]:
            return self._get_by_key(self.deck_data, "name", name)

        def get_game_by_name(self, name: str) -> dict[str, Any]:
            return self._get_by_key(self.game_data, "name", name)
        
        '''
        def get_deck_cards_by_deck_id(self, deck_id: int) -> list[dict[str, Any]]:
            """Get all deck_card data for a specific deck."""
            return [dc for dc in self.deck_card_data if dc["deck_id"] == deck_id]
        '''

        def _pick_random(self, data_list, data_type, attr):
            if len(self.already_picked[data_type]) == len(data_list):
                raise ValueError(f"All {data_type}s have been picked")
            item = random.choice(data_list)
            while item[attr] in self.already_picked[data_type]:
                item = random.choice(data_list)
            self.already_picked[data_type].add(item[attr])
            return item

        @property
        def game(self) -> dict[str, Any]:
            return self._pick_random(self.game_data, "games", "name")

        @property
        def card(self) -> dict[str, Any]:
            return self._pick_random(self.card_data, "cards", "name")

        @property
        def user(self) -> dict[str, Any]:
            return self._pick_random(self.user_data, "users", "username")

        @property
        def deck(self) -> dict[str, Any]:
            return self._pick_random(self.deck_data, "decks", "name")


    return TestData()

