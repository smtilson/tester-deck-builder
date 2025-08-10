# fast_backend/tests/test_decks.py

import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

# Import the actual ORM models you'll be patching
from fast_backend.app.models.users import User as UserORM
from fast_backend.app.models.cards import Card as CardORM
from fast_backend.app.models.decks import Deck as DeckORM
from fast_backend.app.models.deck_cards import DeckCard as DeckCardORM


@pytest.fixture(scope="function")
def mock_orm_models_container():
    """
    Provides an empty, mutable dictionary container for mock ORM data.
    Each test function will populate this dictionary.
    """
    # This dictionary will be reset for each test function due to `function` scope
    return {
        "users": [],
        "cards": [],
        "decks": [],
        "deck_cards": [],
    }


@pytest.fixture(scope="function")
def mock_orm_models_for_test_decks(mock_orm_models_container):
    """
    Patches the .all() and .get() methods of Tortoise ORM models
    to read from the `mock_orm_models_container`.
    """

    # Helper to find an item in a list of dicts based on kwargs
    def find_item(data_list, **kwargs):
        for item in data_list:
            if all(item.get(k) == v for k, v in kwargs.items()):
                return item
        return None

    # Patch the ORM models. These patches will read from the `mock_orm_models_container`.
    with patch.object(DeckORM, "all", new_callable=AsyncMock) as mock_deck_all:
        mock_deck_all.return_value = mock_orm_models_container["decks"]
        with patch.object(DeckORM, "get", new_callable=AsyncMock) as mock_deck_get:
            mock_deck_get.side_effect = lambda **kwargs: find_item(
                mock_orm_models_container["decks"], **kwargs
            )
            yield mock_orm_models_container


# --- Test Class for Endpoint Unit Tests (uses mock ORM) ---
@pytest.mark.skip("standard")
@pytest.mark.usefixtures("override_app_dependencies")  # Global app dependency mocks
class TestDeckEndpointsUnit:
    """
    Unit tests for deck endpoints, where each test populates its own mock database.
    """

    def test_get_all_decks_empty(
        self,
        client,
        mock_orm_models_for_test_decks,  # This fixture provides the mutable mock db container
    ):
        """
        Tests GET /api/decks when no decks are present.
        """
        # mock_orm_models_for_test_decks is initially empty because it's a new fixture instance
        response = client.get("/api/decks")

        assert response.status_code == 200
        assert response.json() == []  # Expect an empty list

    def test_get_all_decks_with_data(
        self,
        client,
        mock_orm_models_for_test_decks,  # This fixture provides the mutable mock db container
    ):
        """
        Tests GET /api/decks when decks are present.
        This test populates the mock database with specific data.
        """
        # --- Populate the mock database for this specific test ---
        user_id_val = uuid.UUID("a0000000-0000-0000-0000-000000000001")
        mock_orm_models_for_test_decks["users"].append(
            {
                "id": user_id_val,
                "username": "testuser1",
                "email": "test1@example.com",
                "name": "Test User One",
                "is_active": True,
                "is_verified": True,
                "is_superuser": False,
                "hashed_password": "mock_hashed_password_1",
            }
        )

        deck_id_1 = uuid.UUID("b0000000-0000-0000-0000-000000000001")
        deck_id_2 = uuid.UUID("b0000000-0000-0000-0000-000000000002")

        mock_orm_models_for_test_decks["decks"].extend(
            [
                {
                    "id": deck_id_1,
                    "name": "Aggro Lightning",
                    "description": "A fast deck with lots of damage.",
                    "is_valid": True,
                    "owner_id": int(user_id_val.hex[:7], 16),
                },
                {
                    "id": deck_id_2,
                    "name": "Green Ramp",
                    "description": "Build up mana to play big creatures.",
                    "is_valid": True,
                    "owner_id": int(user_id_val.hex[:7], 16),
                },
            ]
        )

        # --- Hit the endpoint ---
        response = client.get("/api/decks")

        # --- Assertions ---
        assert response.status_code == 200
        response_json = response.json()

        assert len(response_json) == 2
        assert response_json[0]["id"] == str(deck_id_1)
        assert response_json[0]["name"] == "Aggro Lightning"
        assert response_json[1]["id"] == str(deck_id_2)
        assert response_json[1]["name"] == "Green Ramp"

    def test_get_single_deck_success(self, client, mock_orm_models_for_test_decks):
        """
        Tests GET /api/decks/{deck_id} for a successful retrieval.
        """
        # --- Populate the mock database for this specific test ---
        user_id_val = uuid.UUID("a0000000-0000-0000-0000-000000000001")
        mock_orm_models_for_test_decks["users"].append(
            {
                "id": user_id_val,
                "username": "testuser1",
                "email": "test1@example.com",
                "name": "Test User One",
                "is_active": True,
                "is_verified": True,
                "is_superuser": False,
                "hashed_password": "mock_hashed_password_1",
            }
        )

        deck_id_to_find = uuid.UUID("b0000000-0000-0000-0000-000000000003")
        mock_deck_data = {
            "id": deck_id_to_find,
            "name": "Solo Test Deck",
            "description": "A deck for testing single retrieval.",
            "is_valid": True,
            "owner_id": int(user_id_val.hex[:7], 16),
        }
        mock_orm_models_for_test_decks["decks"].append(mock_deck_data)

        # --- Hit the endpoint ---
        response = client.get(f"/api/decks/{deck_id_to_find}")

        # --- Assertions ---
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["id"] == str(deck_id_to_find)
        assert response_json["name"] == mock_deck_data["name"]
        assert response_json["description"] == mock_deck_data["description"]

    def test_get_single_deck_not_found(self, client, mock_orm_models_for_test_decks):
        """
        Tests GET /api/decks/{deck_id} when the deck is not found.
        """
        # No data needs to be added for this test, as we expect nothing to be found.
        non_existent_id = uuid.UUID("c0000000-0000-0000-0000-000000000001")

        # --- Hit the endpoint ---
        response = client.get(f"/api/decks/{non_existent_id}")

        # --- Assertions ---
        assert response.status_code == 404
        assert response.json() == {"detail": "Deck not found"}
