import uuid
from datetime import datetime
from typing import Dict, List, Any


class BaseTestData:
    """Base test class providing test data for users, cards, decks, and deck_cards."""
    
    def setup_test_data(self):
        """Initialize all test data lists."""
        self.user_data = self._create_user_data()
        self.card_data = self._create_card_data()
        self.deck_data = self._create_deck_data()
        self.deck_card_data = self._create_deck_card_data()
    
    def _create_user_data(self) -> List[Dict[str, Any]]:
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
    
    def _create_card_data(self) -> List[Dict[str, Any]]:
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
    
    def _create_deck_data(self) -> List[Dict[str, Any]]:
        """Create test deck data for database creation."""
        # Use the first user as the default owner
        default_owner_id = self.user_data[0]["id"]
        admin_owner_id = self.user_data[1]["id"]
        
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
    
    def _create_deck_card_data(self) -> List[Dict[str, Any]]:
        """Create test deck_card data for database creation."""
        return [
            {
                "id": 1,
                "deck_id": 1,  # Red Burn Deck
                "card_id": 1,  # Lightning Bolt
                "quantity": 4,
            },
            {
                "id": 2,
                "deck_id": 1,  # Red Burn Deck
                "card_id": 4,  # Basic Land
                "quantity": 20,
            },
            {
                "id": 3,
                "deck_id": 2,  # Blue Control
                "card_id": 3,  # Counterspell
                "quantity": 4,
            },
            {
                "id": 4,
                "deck_id": 2,  # Blue Control
                "card_id": 4,  # Basic Land
                "quantity": 24,
            },
            {
                "id": 5,
                "deck_id": 3,  # Work in Progress
                "card_id": 2,  # Giant Growth
                "quantity": 2,
            },
        ]
    
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
