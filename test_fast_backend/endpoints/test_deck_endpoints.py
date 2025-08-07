'''import pytest
from uuid import UUID
from unittest.mock import AsyncMock, MagicMock, patch

# The `client` fixture and all ORM mocks are provided by conftest.py

MOCK_DB = {"card":[], "deck":[], "deck_card":[], "user":[]}

#@pytest.fixture
def mock_add_db_data(data):
    type = data["type"]
    del data["type"]  # Remove type from data to avoid duplication
    MOCK_DB[type].append(MagicMock(**data))

def test_get_all_decks(client, mock_db_data):
    """
    Tests the GET /decks endpoint to ensure it returns the correct list of decks.
    This test does NOT involve authentication.
    """
    response = client.get("/decks") # Assuming your decks router is mounted at /decks

    assert response.status_code == 200
    response_json = response.json()

    # Assert that the number of decks returned matches your mock data
    assert len(response_json) == len(mock_db_data["decks"])

    # Assert that the data in the response matches your mock data
    # You might need to adjust this based on the exact Pydantic schema
    # your endpoint returns for a Deck.
    for i, deck_data in enumerate(mock_db_data["decks"]):
        assert response_json[i]["id"] == str(deck_data.id) # UUIDs are usually stringified in JSON
        assert response_json[i]["name"] == deck_data.name
        assert response_json[i]["description"] == deck_data.description
        assert response_json[i]["is_valid"] == deck_data.is_valid
        # Note: owner_id might be an int or UUID depending on your schema
        # If it's a relationship that gets populated, you'd check for 'owner' object
        assert response_json[i]["owner_id"] == deck_data.owner_id
'''

# fast_backend/tests/test_decks.py (create this new file)
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
def deck_test_data():
    """
    Provides mock ORM objects for users, cards, decks, and deck_cards.
    This fixture runs for each test function, providing a fresh, isolated dataset.
    """
    # --- Define your mock data for this specific test run ---
    mock_user_1 = MagicMock(
        id=uuid.UUID("a0000000-0000-0000-0000-000000000001"),
        username="testuser1",
        email="test1@example.com",
        name="Test User One",
        is_active=True,
        is_verified=True,
        is_superuser=False,
        hashed_password="mock_hashed_password_1",
    )
    mock_card_1 = MagicMock(id=1, name="Lightning Bolt", text="Deal 3 damage.")
    mock_card_2 = MagicMock(id=2, name="Forest Guardian", text="Defender.")

    mock_deck_1 = MagicMock(
        id=uuid.UUID("b0000000-0000-0000-0000-000000000001"),
        name="Aggro Lightning",
        description="A fast deck with lots of damage.",
        is_valid=True,
        owner_id=int(
            mock_user_1.id.hex[:7], 16
        ),  # Ensure owner_id matches expected type/value
        owner=mock_user_1,  # For prefetch_related scenarios
    )
    mock_deck_2 = MagicMock(
        id=uuid.UUID("b0000000-0000-0000-0000-000000000002"),
        name="Green Ramp",
        description="Build up mana to play big creatures.",
        is_valid=True,
        owner_id=int(mock_user_1.id.hex[:7], 16),  # Same owner for simplicity
        owner=mock_user_1,
    )

    mock_deck_card_1 = MagicMock(
        deck_id=mock_deck_1.id, card_id=mock_card_1.id, quantity=4
    )
    mock_deck_card_2 = MagicMock(
        deck_id=mock_deck_1.id, card_id=mock_card_2.id, quantity=2
    )

    # Return the mock data dictionary to the test
    return {
        "users": [mock_user_1],
        "cards": [mock_card_1, mock_card_2],
        "decks": [mock_deck_1, mock_deck_2],
        "deck_cards": [mock_deck_card_1, mock_deck_card_2],
    }


@pytest.fixture(scope="function")
def mock_orm_models_for_test_decks(deck_test_data):
    """
    Patches the .all() and .get() methods of Tortoise ORM models
    to return specific mock data from the `deck_test_data` fixture.
    This ensures the endpoint interacts with our controlled mock data.
    """
    # Patch the ORM models.
    # We use nested patches to ensure they are all active within the fixture's scope.
    # When the test finishes, these patches are automatically reverted.
    with patch.object(UserORM, "all", new_callable=AsyncMock) as mock_user_all:
        mock_user_all.return_value = deck_test_data["users"]
        with patch.object(UserORM, "get", new_callable=AsyncMock) as mock_user_get:
            # Side effect to simulate .get() behavior based on mock data
            mock_user_get.side_effect = lambda **kwargs: next(
                (
                    u
                    for u in deck_test_data["users"]
                    if all(getattr(u, k) == v for k, v in kwargs.items())
                ),
                None,
            )
            with patch.object(CardORM, "all", new_callable=AsyncMock) as mock_card_all:
                mock_card_all.return_value = deck_test_data["cards"]
                with patch.object(
                    CardORM, "get", new_callable=AsyncMock
                ) as mock_card_get:
                    mock_card_get.side_effect = lambda **kwargs: next(
                        (
                            c
                            for c in deck_test_data["cards"]
                            if all(getattr(c, k) == v for k, v in kwargs.items())
                        ),
                        None,
                    )
                    with patch.object(
                        DeckORM, "all", new_callable=AsyncMock
                    ) as mock_deck_all:
                        mock_deck_all.return_value = deck_test_data["decks"]
                        with patch.object(
                            DeckORM, "get", new_callable=AsyncMock
                        ) as mock_deck_get:
                            mock_deck_get.side_effect = lambda **kwargs: next(
                                (
                                    d
                                    for d in deck_test_data["decks"]
                                    if all(
                                        getattr(d, k) == v for k, v in kwargs.items()
                                    )
                                ),
                                None,
                            )
                            with patch.object(
                                DeckCardORM, "all", new_callable=AsyncMock
                            ) as mock_deck_card_all:
                                mock_deck_card_all.return_value = deck_test_data[
                                    "deck_cards"
                                ]
                                with patch.object(
                                    DeckCardORM, "get", new_callable=AsyncMock
                                ) as mock_deck_card_get:
                                    mock_deck_card_get.side_effect = (
                                        lambda **kwargs: next(
                                            (
                                                dc
                                                for dc in deck_test_data["deck_cards"]
                                                if all(
                                                    getattr(dc, k) == v
                                                    for k, v in kwargs.items()
                                                )
                                            ),
                                            None,
                                        )
                                    )
                                    # Yield the mock data so tests can access it
                                    yield deck_test_data  # Yield the dictionary of mock data

@pytest.mark.usefixtures("override_app_dependencies")
class TestDeckEndpoints:

    def test_get_all_decks(self, client, mock_orm_models_for_test_decks):
        """
        Tests the GET /decks endpoint to ensure it returns the correct list of decks.
        This test does NOT involve authentication.
        """
        response = client.get(
            "/api/decks"
        )  # Assuming your decks router is mounted at /decks

        assert response.status_code == 200
        response_json = response.json()

        # Assert that the number of decks returned matches your mock data
        assert len(response_json) == len(mock_orm_models_for_test_decks["decks"])

        # Assert that the data in the response matches your mock data
        # You might need to adjust this based on the exact Pydantic schema
        # your endpoint returns for a Deck.
        for i, deck_data in enumerate(mock_orm_models_for_test_decks["decks"]):
            assert response_json[i]["id"] == str(
                deck_data.id
            )  # UUIDs are usually stringified in JSON
            assert response_json[i]["name"] == deck_data.name
            assert response_json[i]["description"] == deck_data.description
            assert response_json[i]["is_valid"] == deck_data.is_valid
            # Note: owner_id might be an int or UUID depending on your schema
            # If it's a relationship that gets populated, you'd check for 'owner' object
            assert response_json[i]["owner_id"] == deck_data.owner_id
