import pytest_asyncio
import random

from fast_backend.app.crud.cards import CardRepo
from fast_backend.app.crud.decks import DeckRepo
from fast_backend.app.crud.cards import CardRepo
from fast_backend.app.crud.users import UserRepo
from fast_backend.app.schemas.cards import CardCreate
from fast_backend.app.schemas.decks import DeckCreate
from fast_backend.app.schemas.users import UserCreate


@pytest_asyncio.fixture(scope="function")
async def setup_cards(init_db, card_test_data):
    """Create test cards for read operations."""
    created_cards = []
    for card_data in card_test_data:
        card_create = CardCreate(name=card_data["name"], text=card_data["text"])
        created_card = await CardRepo.create_card(card_create)
        created_cards.append(created_card)
    return created_cards


@pytest_asyncio.fixture(scope="function")
async def single_card(init_db, card_test_data):
    """Create a test card for update operations."""
    card_data = random.choice(card_test_data)
    while None in card_data.values():
        card_data = random.choice(card_test_data)
    card_create = CardCreate(**card_data)
    test_card = await CardRepo.create_card(card_create)
    return test_card


@pytest_asyncio.fixture(scope="function")
async def single_deck_and_cards(
    init_db, card_test_data, deck_test_data, user_test_data
):
    """Create test deck and cards for deck_card operations."""
    # Create user
    user_data = user_test_data[0]  # testuser1
    owner = await UserRepo.create_user(UserCreate(**user_data))

    # Create deck
    deck_data = deck_test_data[0]  # Red Burn Deck
    deck_create = DeckCreate(
        name=deck_data["name"],
        description=deck_data["description"],
        is_valid=deck_data["is_valid"],
        owner=owner,
    )
    test_deck = await DeckRepo.create_deck_record(deck_create)

    # Create cards
    test_cards = []
    for card_data in card_test_data:
        card_create = CardCreate(name=card_data["name"], text=card_data["text"])
        created_card = await CardRepo.create_card(card_create)
        test_cards.append(created_card)

    return {"owner": owner, "test_deck": test_deck, "test_cards": test_cards}


@pytest_asyncio.fixture(scope="function")
async def setup_decks(init_db, setup_users, deck_test_data):
    """Create test decks for read operations."""
    # Create owners first
    user1 = random.choice(setup_users)
    user2 = random.choice([user for user in setup_users if user.id != user1.id])

    # Create decks
    created_decks = []
    for deck_data in deck_test_data:
        deck_data["owner"] = random.choice([user1, user2])
        deck_create = DeckCreate(**deck_data)
        created_deck = await DeckRepo.create_deck_record(deck_create)
        created_decks.append(created_deck)
    return created_decks


@pytest_asyncio.fixture(scope="function")
async def single_deck(init_db, deck_test_data, single_user):
    """Create a test deck for update operations."""
    deck_data = random.choice(deck_test_data)
    deck_data["owner"] = single_user
    deck_create = DeckCreate(**deck_data)
    test_deck = await DeckRepo.create_deck_record(deck_create)
    return {"owner": single_user, "test_deck": test_deck}


@pytest_asyncio.fixture(scope="function")
async def setup_users(init_db, user_test_data):
    """Create test users for read operations."""
    created_users = []
    for user_data in user_test_data:
        user_create = UserCreate(**user_data)
        created_user = await UserRepo.create_user(user_create)
        created_users.append(created_user)
    return created_users


@pytest_asyncio.fixture(scope="function")
async def single_user(init_db, user_test_data):
    """Create a test user for update operations."""
    user_data = random.choice(user_test_data)
    user_create = UserCreate(**user_data)
    test_user = await UserRepo.create_user(user_create)
    print(test_user)
    print(type(test_user))
    return test_user


@pytest_asyncio.fixture(scope="function")
async def setup_admin(init_db, user_test_data):
    """Create test users with different admin statuses."""
    # Select one admin and one regular user randomly
    user_data = random.choice(user_test_data)
    user_data["is_admin"] = True
    admin_user = await UserRepo.create_user(UserCreate(**user_data))
    return admin_user
