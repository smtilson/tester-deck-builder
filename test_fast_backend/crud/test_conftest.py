import pytest
import pytest_asyncio
from fast_backend.app.schemas.users import UserResponse
from fast_backend.app.schemas.games import GameResponse
from fast_backend.app.schemas.cards import CardResponse
from fast_backend.app.schemas.decks import DeckResponse
from fast_backend.app.models.users import User
from fast_backend.app.models.games import Game
from fast_backend.app.models.cards import Card
from fast_backend.app.models.decks import Deck

"""This is designed to test the CRUD conftest fixtures."""

@pytest.mark.asyncio
async def test_single_user_fixture(single_user, all_test_data):
    """Test that single_user fixture returns a user with all required properties."""
    assert single_user is not None
    # Check required UserResponse fields
    for field in UserResponse.model_fields:
        assert hasattr(single_user, field)
    # Check user exists in DB
    db_user = await User.get(single_user.id)
    assert db_user is not None
    assert db_user.username == single_user.username

@pytest.mark.asyncio
async def test_single_game_fixture(single_game, all_test_data):
    """Test that single_game fixture returns a game with all required properties."""
    assert single_game is not None
    for field in GameResponse.model_fields:
        assert hasattr(single_game, field)
    db_game = await Game.get(single_game.id)
    assert db_game is not None
    assert db_game.name == single_game.name

@pytest.mark.asyncio
async def test_single_card_fixture(single_card, all_test_data):
    """Test that single_card fixture returns a card with all required properties."""
    assert single_card is not None
    for field in CardResponse.model_fields:
        assert hasattr(single_card, field)
    db_card = await Card.get(single_card.id)
    assert db_card is not None
    assert db_card.name == single_card.name

@pytest.mark.asyncio
async def test_single_deck_no_cards_fixture(single_deck_no_cards, all_test_data):
    """Test that single_deck_no_cards fixture returns a deck with all required properties."""
    assert single_deck_no_cards is not None
    for field in DeckResponse.model_fields:
        assert hasattr(single_deck_no_cards, field)
    db_deck = await Deck.get(single_deck_no_cards.id)
    assert db_deck is not None
    assert db_deck.name == single_deck_no_cards.name

@pytest.mark.asyncio
async def test_setup_users_fixture(setup_users, all_test_data):
    """Test that setup_users fixture creates the correct number of users and all have required properties."""
    assert setup_users is not None
    assert len(setup_users) == len(all_test_data.user_data)
    user_ids = [user.id for user in setup_users]
    db_users = await User.find(User.id.in_(user_ids)).to_list()
    assert len(db_users) == len(all_test_data.user_data)
    for user in setup_users:
        for field in UserResponse.model_fields:
            assert hasattr(user, field)

