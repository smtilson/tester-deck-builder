import pytest_asyncio
import random


# all managers are fixtures

async def _create_single_item(manager, item_data):
    return await manager.create_from_dict(item_data)

# --- Single Item Fixtures ---
@pytest_asyncio.fixture(scope="function")
async def single_user(init_db, all_test_data, user_manager):
    """Create a test user for update operations."""
    user_data = all_test_data.user
    return await _create_single_item(user_manager, user_data)

@pytest_asyncio.fixture(scope="function")
async def single_game(init_db, all_test_data, game_manager, setup_users):
    """Create a test game for update operations."""
    game_data = all_test_data.game
    num_designers = random.randint(1, len(setup_users))
    num_developers = random.randint(1, len(setup_users))
    designer_ids = list({user.id for user in random.sample(setup_users, num_designers)})
    developer_ids = list({user.id for user in random.sample(setup_users, num_developers)})
    game_data["designer_ids"] = designer_ids
    game_data["developer_ids"] = developer_ids
    return await _create_single_item(game_manager, game_data)

@pytest_asyncio.fixture(scope="function")
async def single_card(init_db, all_test_data, single_game, card_manager):
    """Create a test card for update operations."""
    card_data = all_test_data.card
    card_data["game_id"] = single_game.id
    return await _create_single_item(card_manager, card_data)

@pytest_asyncio.fixture(scope="function")
async def single_deck_no_cards(init_db, all_test_data, single_game, single_user, deck_manager):
    deck_data = all_test_data.deck
    deck_data["owner_id"] = single_user.id
    deck_data["game_id"] = single_game.id
    return await _create_single_item(deck_manager, deck_data)

# --- Multiple Item Fixtures ---

@pytest_asyncio.fixture(scope="function")
async def setup_users(init_db, user_manager, user_test_data):
    """Create test users for read operations."""
    users = []
    for user_data in user_test_data:
        user = await user_manager.create_from_dict(user_data)
        users.append(user)
    return users


@pytest_asyncio.fixture(scope="function")
async def setup_games(init_db, game_manager, game_test_data, setup_users):
    """Create test games for read operations."""
    games = []
    for game_data in game_test_data:
        num1 = random.randint(1,len(setup_users))
        num2 = random.randint(1,len(setup_users))
        designer_ids = list({user.id for user in random.sample(setup_users, num1)})
        developer_ids = list({user.id for user in random.sample(setup_users, num2)})
        game_data["designer_ids"] = designer_ids
        game_data["developer_ids"] = developer_ids
        created_game = await game_manager.create_from_dict(game_data)
        games.append(created_game)
    return games
    


@pytest_asyncio.fixture(scope="function")
async def setup_cards(init_db, card_manager,
                    card_test_data, setup_games):
    """Create test cards for read operations."""
    cards = []
    for card_data in card_test_data:
        card_data["game_id"] = random.choice(setup_games).id
        created_card = await card_manager.create_from_dict(card_data)
        cards.append(created_card)
    return cards

@pytest_asyncio.fixture(scope="function")
async def setup_decks_no_cards(init_db, deck_manager, 
                            deck_test_data, setup_users, setup_games):
    """Create test decks for read operations."""
    # Create decks
    created_decks = []
    for deck_data in deck_test_data:
        deck_data["owner_id"] = random.choice(setup_users).id
        deck_data["game_id"] = random.choice(setup_games).id
        created_deck = await deck_manager.create_from_dict(deck_data)
        created_decks.append(created_deck)
    return created_decks
