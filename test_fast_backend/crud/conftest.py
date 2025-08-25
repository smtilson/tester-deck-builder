import pytest_asyncio
import random


# user_manager is a fixture
from fast_backend.app.schemas.cards import CardCreate
from fast_backend.app.schemas.decks import DeckCreate
from fast_backend.app.schemas.games import GameCreate
from fast_backend.app.schemas.users import UserCreate


async def _create_single_item(manager, create_schema, item_data):
    item_create = create_schema(**item_data)
    created_item = await manager.create(item_create)
    return created_item

async def _create_many_items(_single_item, num_items):
    created_items = []
    for _ in range(num_items):
        created_item = await _single_item
        created_items.append(created_item)
    return created_items


# --- Single Item Fixtures ---
@pytest_asyncio.fixture(scope="function")
async def single_user(init_db, all_test_data, user_manager):
    """Create a test user for update operations."""
    return await _create_single_item(user_manager, UserCreate, all_test_data.user)

@pytest_asyncio.fixture(scope="function")
async def single_game(init_db, all_test_data, game_manager, single_user):
    """Create a test game for update operations."""
    game_data = all_test_data.game
    num_designers = random.randint(1, 4)
    num_developers = random.randint(1, 4)
    designer_ids = [single_user.id for _ in range(num_designers)]
    developer_ids = [single_user.id for _ in range(num_developers)]
    game_data["designers"] = designer_ids
    game_data["developers"] = developer_ids
    return await _create_single_item(game_manager, GameCreate, game_data)

@pytest_asyncio.fixture(scope="function")
async def single_card(init_db, all_test_data, single_game, card_manager):
    """Create a test card for update operations."""
    card_data = all_test_data.card
    card_data["game_id"] = single_game.id
    return await _create_single_item(card_manager, CardCreate, card_data)

@pytest_asyncio.fixture(scope="function")
async def single_deck_no_cards(init_db, all_test_data, single_game, single_user, deck_manager):
    deck_data = all_test_data.deck
    deck_data["owner_id"] = single_user.id
    deck_data["game_id"] = single_game.id
    return await _create_single_item(deck_manager, DeckCreate, deck_data)

@pytest_asyncio.fixture(scope="function")
async def setup_users(init_db, single_user, all_test_data):
    """Create test users for read operations."""
    return await _create_many_items(single_user, len(all_test_data.user_data))


@pytest_asyncio.fixture(scope="function")
async def setup_games(init_db, all_test_data, single_game):
    """Create test games for read operations."""
    games = []
    num_games = len(all_test_data.game_data)
    for _ in range(num_games):
        game = await single_game
        games.append(game)
    return games


@pytest_asyncio.fixture(scope="function")
async def setup_cards(init_db, all_test_data, single_card):
    """Create test cards for read operations."""
    cards = []
    num_cards = len(all_test_data.card_data)
    for _ in range(num_cards):
        card = await single_card
        cards.append(card)
    return cards

@pytest_asyncio.fixture(scope="function")
async def setup_decks_no_cards(init_db, setup_users, all_test_data):
    """Create test decks for read operations."""
    # Create owners first
    user1 = await UserManager.create_user(UserCreate(**all_test_data.user))
    user2 = await UserManager.create_user(UserCreate(**all_test_data.user))

    # Create decks
    created_decks = []
    for deck_data in all_test_data.deck_data:
        deck_data["owner"] = random.choice([user1, user2])
        deck_create = DeckCreate(**deck_data)
        created_deck = await deck_manager.create_deck_record(deck_create)
        created_decks.append(created_deck)
    return created_decks




@pytest_asyncio.fixture(scope="function")
async def setup_admin(init_db, all_test_data, user_manager):
    """Create test users with different admin statuses."""
    # Select one admin and one regular user randomly
    user_data = all_test_data.user
    user_data["is_admin"] = True
    admin_user = await user_manager.create(UserCreate(**user_data))
    return admin_user
