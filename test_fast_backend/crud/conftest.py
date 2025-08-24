import pytest_asyncio
import random

from fast_backend.app.crud.cards import card_manager
from fast_backend.app.crud.decks import deck_manager
from fast_backend.app.crud.deck_cards import deck_card_manager
from fast_backend.app.crud.games import game_manager
from fast_backend.app.crud.users import UserManager
from fast_backend.app.schemas.cards import CardCreate
from fast_backend.app.schemas.decks import DeckCreate
from fast_backend.app.schemas.games import GameCreate
from fast_backend.app.schemas.users import UserCreate


#@pytest_asyncio.fixture(scope="function")
async def _setup_items(create_schema, item_manager, item_data):
    created_items = []
    for datum in item_data:
        item_create = create_schema(**datum)
        created_item = await item_manager.create(item_create)
        created_items.append(created_item)
    return created_items

#@pytest_asyncio.fixture(scope="function")
async def _single_item(create_schema, item_manager, datum):
    item_create = create_schema(**datum)
    created_item = await item_manager.create(item_create)
    return created_item

@pytest_asyncio.fixture(scope="function")
async def setup_users(init_db, all_test_data, user_manager):
    """Create test users for read operations."""
    return await _setup_items(UserCreate, user_manager, all_test_data.user_data)

@pytest_asyncio.fixture(scope="function")
async def single_user(init_db, all_test_data, user_manager):
    """Create a test user for update operations."""
    return await _single_item(UserCreate, user_manager, all_test_data.user)

@pytest_asyncio.fixture(scope="function")
async def setup_games(init_db, all_test_data):
    """Create test games for read operations."""
    return await _setup_items(GameCreate, game_manager, all_test_data.game_data)

@pytest_asyncio.fixture(scope="function")
async def single_game(init_db, all_test_data):
    """Create a test game for update operations."""
    return await _single_item(GameCreate, game_manager, all_test_data.game)

@pytest_asyncio.fixture(scope="function")
async def setup_cards(init_db, all_test_data):
    """Create test cards for read operations."""
    return await _setup_items(CardCreate, card_manager, all_test_data.card_data)

@pytest_asyncio.fixture(scope="function")
async def single_card(init_db, all_test_data):
    """Create a test card for update operations."""
    return await _single_item(CardCreate, card_manager, all_test_data.card)

    

@pytest_asyncio.fixture(scope="function")
async def setup_decks(init_db, setup_users, all_test_data):
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
async def single_deck(init_db, all_test_data, single_user):
    """Create a test deck for update operations."""
    deck_data = all_test_data.deck
    deck_data["owner"] = single_user
    deck_create = DeckCreate(**deck_data)
    test_deck = await deck_manager.create_deck_record(deck_create)
    return {"owner": single_user, "test_deck": test_deck}




@pytest_asyncio.fixture(scope="function")
async def setup_admin(init_db, all_test_data):
    """Create test users with different admin statuses."""
    # Select one admin and one regular user randomly
    user_data = all_test_data.user
    user_data["is_admin"] = True
    admin_user = await UserManager.create_user(UserCreate(**user_data))
    return admin_user
