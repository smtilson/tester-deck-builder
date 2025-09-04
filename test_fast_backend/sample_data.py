import pytest
import copy
import random
from typing import Any, List, Dict, Optional
from datetime import datetime

# --- Fixtures for test data ---

@pytest.fixture
def user_test_data() -> List[Dict[str, str]]:
    """Create test user data for database creation."""
    return [
        {"username": "testuser1", "email": "test1@example.com", "password": "password123", "confirm_password": "password123"},
        {"username": "admin_user", "email": "admin@example.com", "password": "adminpass123", "confirm_password": "adminpass123"},
        {"username": "inactive_user", "email": "inactive@example.com", "password": "password123", "confirm_password": "password123"},
        {"username": "player_two", "email": "player2@example.com", "password": "player2pass", "confirm_password": "player2pass"},
        {"username": "deck_builder", "email": "builder@example.com", "password": "builderpass", "confirm_password": "builderpass"},
        {"username": "guest_user", "email": "guest@example.com", "password": "guestpass", "confirm_password": "guestpass"},
    ]

@pytest.fixture
def card_test_data() -> List[Dict[str, str]]:
    """Create test card data for database creation."""
    return [
        {"name": "Lightning Bolt", "text": "Lightning Bolt deals 3 damage to any target."},
        {"name": "Giant Growth", "text": "Target creature gets +3/+3 until end of turn."},
        {"name": "Counterspell", "text": "Counter target spell."},
        {"name": "Basic Land", "text": "not none"},
        {"name": "Serra Angel", "text": "Flying, vigilance"},
        {"name": "Dark Ritual", "text": "Add three black mana."},
        {"name": "Wrath of God", "text": "Destroy all creatures."},
    ]

@pytest.fixture
def deck_test_data() -> List[Dict[str, str]]:
    """Create test deck data for database creation."""
    return [
        {"name": "Red Burn Deck", "description": "A fast aggressive red deck focused on dealing damage quickly."},
        {"name": "Blue Control", "description": "A control deck that counters spells and draws cards."},
        {"name": "Work in Progress", "description": "An incomplete deck still being built."},
        {"name": "Green Ramp", "description": "A deck focused on ramping mana and playing big creatures."},
        {"name": "Black Discard", "description": "A deck that forces opponents to discard cards."},
        {"name": "White Weenie", "description": "A deck with lots of small, efficient creatures."},
    ]

@pytest.fixture
def game_test_data() -> List[Dict[str, Any]]:
    """Create test game data for database creation based on Game model."""
    return [
        {
            "name": "Magic: The Gathering",
            "version": "1.0.0",
            "description": "A collectible card game created by Richard Garfield.",
            "designer_ids": [],
            "publisher": "Wizards of the Coast",
            "developer_ids": [],
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
        {
            "name": "KeyForge",
            "version": "1.0.0",
            "description": "A unique deck game by Richard Garfield.",
            "designer_ids": [],
            "publisher": "Fantasy Flight Games",
            "developer_ids": [],
            "release_date": datetime(2018, 11, 15),
        },
        {
            "name": "Legend of the Five Rings",
            "version": "4.0.0",
            "description": "A game of samurai and honor.",
            "designer_ids": [],
            "publisher": "Fantasy Flight Games",
            "developer_ids": [],
            "release_date": datetime(2017, 10, 5),
        },
        {
            "name": "Android: Netrunner",
            "version": "2.0.0",
            "description": "A cyberpunk card game.",
            "designer_ids": [],
            "publisher": "Fantasy Flight Games",
            "developer_ids": [],
            "release_date": datetime(2012, 8, 17),
        },
    ]

class DataDict:
    """Helper class for managing and picking test data."""

    def __init__(
        self,
        users: List[Dict[str, Any]],
        games: List[Dict[str, Any]],
        cards: List[Dict[str, Any]],
        decks: List[Dict[str, Any]],
    ):
        self._users: List[Dict[str, Any]] = users
        self._games: List[Dict[str, Any]] = games
        self._cards: List[Dict[str, Any]] = cards
        self._decks: List[Dict[str, Any]] = decks
        self._picked: Dict[str, List[Dict[str, Any]]] = {
            "users": [],
            "games": [],
            "cards": [],
            "decks": [],
        }

    @property
    def users(self) -> List[Dict[str, Any]]:
        """Return a deep copy of all user data."""
        return copy.deepcopy(self._users)

    @property
    def games(self) -> List[Dict[str, Any]]:
        """Return a deep copy of all game data."""
        return copy.deepcopy(self._games)

    @property
    def cards(self) -> List[Dict[str, Any]]:
        """Return a deep copy of all card data."""
        return copy.deepcopy(self._cards)

    @property
    def decks(self) -> List[Dict[str, Any]]:
        """Return a deep copy of all deck data."""
        return copy.deepcopy(self._decks)

    def _pick_random(self, data_list: List[Dict[str, Any]], key: str) -> Dict[str, Any]:
        """Pick a random item from the list that hasn't been picked yet."""
        available = [item for item in data_list if item not in self._picked[key]]
        if not available:
            raise ValueError(f"All {key} have been picked.")
        choice = random.choice(available)
        self._picked[key].append(choice)
        return copy.deepcopy(choice)

    @property
    def user(self) -> Dict[str, Any]:
        """Pick a random user that hasn't been picked yet."""
        return self._pick_random(self._users, "users")
    
    @property
    def hashed_user(self) -> dict[str, Any]:
        """Pick a random user that hasn't been picked yet."""
        user = self.user
        user["hashed_password"] = "hashed_" + user["password"]
        return user
    
    @property
    def game(self) -> Dict[str, Any]:
        """Pick a random game that hasn't been picked yet."""
        return self._pick_random(self._games, "games")

    @property
    def card(self) -> Dict[str, Any]:
        """Pick a random card that hasn't been picked yet."""
        return self._pick_random(self._cards, "cards")

    @property
    def deck(self) -> Dict[str, Any]:
        """Pick a random deck that hasn't been picked yet."""
        return self._pick_random(self._decks, "decks")

    def _get_by_key(
        self, data_list: List[Dict[str, Any]], key: str, value: Any
    ) -> Dict[str, Any]:
        """Generic method to get an item by key from a list of dicts."""
        for item in data_list:
            if item.get(key, None) == value:
                return item
        raise ValueError(f"{key.capitalize()} with value '{value}' not found")

    def get_user_by_username(self, username: str) -> Dict[str, Any]:
        """Get a user dict by username."""
        return self._get_by_key(self._users, "username", username)

    def get_card_by_name(self, name: str) -> Dict[str, Any]:
        """Get a card dict by name."""
        return self._get_by_key(self._cards, "name", name)

    def get_deck_by_name(self, name: str) -> Dict[str, Any]:
        """Get a deck dict by name."""
        return self._get_by_key(self._decks, "name", name)

    def get_game_by_name(self, name: str) -> Dict[str, Any]:
        """Get a game dict by name."""
        return self._get_by_key(self._games, "name", name)

@pytest.fixture(scope="function")
def data(
    user_test_data: List[Dict[str, Any]],
    game_test_data: List[Dict[str, Any]],
    card_test_data: List[Dict[str, Any]],
    deck_test_data: List[Dict[str, Any]],
) -> DataDict:
    """Fixture that provides a DataDict instance for test data access."""
    return DataDict(user_test_data, game_test_data, card_test_data, deck_test_data)




