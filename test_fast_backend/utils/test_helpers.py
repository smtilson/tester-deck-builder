"""Test helper utilities for common test operations."""
from typing import Dict, Any
from uuid import UUID
from unittest.mock import MagicMock


def create_mock_user(
    id: UUID = UUID("12345678-1234-5678-1234-567812345678"),
    email: str = "test@example.com",
    username: str = "testuser",
    name: str = "Test User",
    is_active: bool = True,
    is_verified: bool = False,
    is_superuser: bool = False,
    is_admin: bool = False,
    **kwargs
) -> MagicMock:
    """Create a mock user object with sensible defaults."""
    mock_user = MagicMock()
    mock_user.id = id
    mock_user.email = email
    mock_user.username = username
    mock_user.name = name
    mock_user.is_active = is_active
    mock_user.is_verified = is_verified
    mock_user.is_superuser = is_superuser
    mock_user.is_admin = is_admin
    mock_user.hashed_password = kwargs.get("hashed_password", "mock_hashed_password")
    mock_user.oauth_accounts = kwargs.get("oauth_accounts", [])
    mock_user.created_at = MagicMock()
    mock_user.updated_at = MagicMock()
    
    # Add any additional attributes
    for key, value in kwargs.items():
        if not hasattr(mock_user, key):
            setattr(mock_user, key, value)
    
    return mock_user


def assert_user_attributes(user, expected_data: Dict[str, Any]):
    """Assert that a user object has the expected attributes."""
    for key, expected_value in expected_data.items():
        actual_value = getattr(user, key)
        assert actual_value == expected_value, f"Expected {key}={expected_value}, got {actual_value}"


def assert_card_attributes(card, expected_data: Dict[str, Any]):
    """Assert that a card object has the expected attributes."""
    for key, expected_value in expected_data.items():
        actual_value = getattr(card, key)
        assert actual_value == expected_value, f"Expected {key}={expected_value}, got {actual_value}"


def assert_deck_attributes(deck, expected_data: Dict[str, Any]):
    """Assert that a deck object has the expected attributes."""
    for key, expected_value in expected_data.items():
        actual_value = getattr(deck, key)
        assert actual_value == expected_value, f"Expected {key}={expected_value}, got {actual_value}"
