"""
Quick database population script for testing and development.

This script creates minimal but sufficient test data quickly:
- 5 test users (including admin)
- 20 basic cards
- 5 sample decks
- Deck-card relationships

Usage:
    python -m app.quick_populate
"""

import asyncio
import uuid
import random

from fastapi_users.password import PasswordHelper

'''
from fast_backend.app.models import User
from fast_backend.app.models import Card
from fast_backend.app.models import Deck
from fast_backend.app.models import DeckCard
from fast_backend.app.db.config_db import init_db, close_db


async def quick_populate():
    """Quickly populate database with minimal test data."""
    print("🚀 Quick database population starting...")

    await init_db()

    try:
        password_helper = PasswordHelper()

        # Clear existing data
        print("🗑️  Clearing existing data...")
        await DeckCard.all().delete()
        await Deck.all().delete()
        await Card.all().delete()
        await User.all().delete()

        # Create test users
        print("👥 Creating test users...")
        users = []

        # Admin user
        admin = await User.create(
            id=uuid.uuid4(),
            username="admin",
            email="admin@test.com",
            hashed_password=password_helper.hash("admin123"),
            name="Administrator",
            is_active=True,
            is_verified=True,
            is_superuser=True,
            is_admin=True,
        )
        users.append(admin)
        print("📝 Admin user: admin@test.com / admin123")

        # Regular test users
        test_users = [
            {"username": "testuser1", "email": "test1@test.com", "name": "Test User 1"},
            {"username": "testuser2", "email": "test2@test.com", "name": "Test User 2"},
            {"username": "testuser3", "email": "test3@test.com", "name": "Test User 3"},
            {
                "username": "deckbuilder",
                "email": "builder@test.com",
                "name": "Deck Builder",
            },
        ]

        for user_data in test_users:
            user = await User.create(
                id=uuid.uuid4(),
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=password_helper.hash("test123"),
                name=user_data["name"],
                is_active=True,
                is_verified=True,
                is_superuser=False,
                is_admin=False,
            )
            users.append(user)

        # Create basic cards
        print("🃏 Creating basic cards...")
        card_data = [
            {"name": "Lightning Bolt", "text": "Deal 3 damage to any target."},
            {
                "name": "Giant Growth",
                "text": "Target creature gets +3/+3 until end of turn.",
            },
            {"name": "Counterspell", "text": "Counter target spell."},
            {"name": "Dark Ritual", "text": "Add 3 black mana."},
            {"name": "Healing Potion", "text": "Gain 5 life."},
            {"name": "Goblin Warrior", "text": "A fierce goblin ready for battle."},
            {"name": "Forest Guardian", "text": "Defender. A protector of nature."},
            {"name": "Fire Dragon", "text": "Flying. A mighty dragon breathing fire."},
            {"name": "Crystal Sword", "text": "Equipment. +2/+2 to equipped creature."},
            {"name": "Magic Shield", "text": "Equipment. +0/+3 to equipped creature."},
            {"name": "Mountain", "text": "Basic land. Tap for red mana."},
            {"name": "Island", "text": "Basic land. Tap for blue mana."},
            {"name": "Forest", "text": "Basic land. Tap for green mana."},
            {"name": "Plains", "text": "Basic land. Tap for white mana."},
            {"name": "Swamp", "text": "Basic land. Tap for black mana."},
            {"name": "Fireball", "text": "Deal X damage to target."},
            {"name": "Time Walk", "text": "Take an extra turn."},
            {"name": "Mind Control", "text": "Gain control of target creature."},
            {"name": "Vampire Lord", "text": "Flying, Lifelink. Lord of vampires."},
            {"name": "Angel of Light", "text": "Flying, Vigilance. Divine protector."},
        ]

        cards = []
        for data in card_data:
            card = await Card.create(**data)
            cards.append(card)

        # Create sample decks
        print("🎴 Creating sample decks...")
        deck_data = [
            {"name": "Red Aggro", "description": "Fast aggressive red deck"},
            {"name": "Blue Control", "description": "Control deck with counterspells"},
            {
                "name": "Green Ramp",
                "description": "Big creatures and mana acceleration",
            },
            {"name": "White Weenie", "description": "Small efficient creatures"},
            {"name": "Black Combo", "description": "Powerful black magic combinations"},
        ]

        decks = []
        for i, data in enumerate(deck_data):
            owner = users[i % len(users)]
            deck = await Deck.create(
                name=data["name"],
                description=data["description"],
                is_valid=random.choice([True, False]),
                owner=owner,
            )
            decks.append(deck)

        # Add cards to decks
        print("🔗 Adding cards to decks...")
        for deck in decks:
            # Each deck gets 10-15 random cards
            deck_cards = random.sample(cards, random.randint(10, 15))
            for card in deck_cards:
                quantity = random.randint(1, 4)
                try:
                    await DeckCard.create(deck=deck, card=card, quantity=quantity)
                except:
                    # Skip if already exists
                    pass

        # Print summary
        print(f"\n✅ Quick population completed!")
        print(f"   Users: {await User.all().count()}")
        print(f"   Cards: {await Card.all().count()}")
        print(f"   Decks: {await Deck.all().count()}")
        print(f"   Deck-Cards: {await DeckCard.all().count()}")
        print(f"\n🔑 Login with: admin@test.com / admin123")

    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(quick_populate())
'''
