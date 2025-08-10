"""
Database population script with dummy data for development and testing.

This script creates realistic sample data for:
- Users (with proper password hashing)
- Cards (various types of game cards)
- Decks (sample deck builds)
- DeckCard relationships (cards in decks with quantities)

Usage:
    python -m app.generate_data
    python -m app.generate_data --users 50 --cards 200 --decks 20
    python -m app.generate_data --clear  # Clear existing data first
"""

import asyncio
import argparse
from typing import List, Dict, Any
import uuid
import random

from tortoise import Tortoise
from fastapi_users.password import PasswordHelper

from fast_backend.app.models.users import User
from fast_backend.app.models.cards import Card
from fast_backend.app.models.decks import Deck
from fast_backend.app.models.deck_cards import DeckCard
from fast_backend.app.db.config_db import init_db, close_db, MODEL_PATHS
from fast_backend.app.core.config_app import settings


# Sample card data inspired by trading card games
SAMPLE_CARDS_DATA = [
    # Creatures
    {
        "name": "Lightning Drake",
        "text": "Flying. When Lightning Drake enters play, deal 2 damage to any target.",
    },
    {"name": "Forest Guardian", "text": "Defender. Regenerate: Pay 1 green mana."},
    {"name": "Goblin Warrior", "text": "Haste. Cannot block."},
    {
        "name": "Ancient Dragon",
        "text": "Flying, Trample. When Ancient Dragon attacks, draw a card.",
    },
    {
        "name": "Knight of Honor",
        "text": "First Strike, Vigilance. Protection from black.",
    },
    {
        "name": "Shadow Assassin",
        "text": "Stealth. When Shadow Assassin deals damage, target opponent discards a card.",
    },
    {
        "name": "Crystal Golem",
        "text": "Artifact Creature. Gets +1/+1 for each artifact you control.",
    },
    {
        "name": "Fire Elemental",
        "text": "When Fire Elemental enters play, deal 3 damage to target creature.",
    },
    {
        "name": "Sea Serpent",
        "text": "Can only attack if defending player controls an island.",
    },
    {"name": "Vampire Lord", "text": "Flying, Lifelink. Other vampires get +1/+1."},
    # Spells
    {"name": "Lightning Bolt", "text": "Deal 3 damage to any target."},
    {"name": "Counterspell", "text": "Counter target spell."},
    {"name": "Giant Growth", "text": "Target creature gets +3/+3 until end of turn."},
    {"name": "Dark Ritual", "text": "Add 3 black mana to your mana pool."},
    {"name": "Healing Potion", "text": "Gain 5 life."},
    {"name": "Mind Control", "text": "Gain control of target creature."},
    {
        "name": "Fireball",
        "text": "Deal X damage to any target, where X is the amount of mana spent.",
    },
    {"name": "Time Walk", "text": "Take an extra turn after this one."},
    {"name": "Wrath of God", "text": "Destroy all creatures."},
    {"name": "Ancestral Recall", "text": "Draw 3 cards."},
    # Artifacts
    {
        "name": "Sword of Power",
        "text": "Equipped creature gets +2/+2. Equip cost: 2 mana.",
    },
    {"name": "Mana Crystal", "text": "Tap: Add 1 colorless mana to your mana pool."},
    {
        "name": "Shield of Defense",
        "text": "Equipped creature gets +0/+3 and defender. Equip cost: 1 mana.",
    },
    {
        "name": "Ring of Wisdom",
        "text": "Equipped creature can draw an extra card each turn. Equip cost: 3 mana.",
    },
    {
        "name": "Boots of Speed",
        "text": "Equipped creature has haste. Equip cost: 1 mana.",
    },
    # Enchantments
    {"name": "Blessing of Light", "text": "All your creatures get +1/+1."},
    {"name": "Curse of Darkness", "text": "All opponent's creatures get -1/-1."},
    {"name": "Mana Surge", "text": "Whenever you play a spell, draw a card."},
    {
        "name": "Nature's Bounty",
        "text": "At the beginning of your turn, gain 1 life for each creature you control.",
    },
    {"name": "Arcane Studies", "text": "Spells cost 1 less mana to cast."},
    # Lands
    {"name": "Mountain", "text": "Tap: Add 1 red mana to your mana pool."},
    {"name": "Island", "text": "Tap: Add 1 blue mana to your mana pool."},
    {"name": "Forest", "text": "Tap: Add 1 green mana to your mana pool."},
    {"name": "Plains", "text": "Tap: Add 1 white mana to your mana pool."},
    {"name": "Swamp", "text": "Tap: Add 1 black mana to your mana pool."},
    {
        "name": "Ancient Library",
        "text": "Tap: Add 1 colorless mana. Pay 2, Tap: Draw a card.",
    },
    {
        "name": "Crystal Caves",
        "text": "Tap: Add 1 mana of any color. Enters play tapped.",
    },
    {"name": "Mystic Temple", "text": "Tap: Add 1 mana of any color. Pay 3: Scry 1."},
]

# Sample deck themes and names
DECK_THEMES = [
    {
        "name": "Lightning Storm",
        "description": "Fast aggressive deck focused on dealing quick damage with lightning spells and creatures.",
    },
    {
        "name": "Forest Defense",
        "description": "Defensive strategy using nature's guardians and healing magic.",
    },
    {
        "name": "Shadow Control",
        "description": "Control the battlefield with dark magic and mind manipulation.",
    },
    {
        "name": "Crystal Power",
        "description": "Artifact-based deck leveraging powerful equipment and constructs.",
    },
    {
        "name": "Dragon's Fury",
        "description": "High-cost, high-reward deck centered around powerful dragons.",
    },
    {
        "name": "Vampire Swarm",
        "description": "Aggressive deck using vampire synergies and life-drain abilities.",
    },
    {
        "name": "Knight's Honor",
        "description": "Midrange deck focused on honorable knights and protection spells.",
    },
    {
        "name": "Elemental Chaos",
        "description": "Unpredictable deck mixing various elemental creatures and spells.",
    },
    {
        "name": "Sea Mastery",
        "description": "Blue-focused deck controlling the game through counterspells and sea creatures.",
    },
    {
        "name": "Goblin Rush",
        "description": "Ultra-fast aggro deck overwhelming opponents with goblin creatures.",
    },
    {
        "name": "Healing Sanctuary",
        "description": "Control deck focused on gaining life and protecting key creatures.",
    },
    {
        "name": "Ancient Wisdom",
        "description": "Spell-heavy deck drawing cards and casting powerful magic.",
    },
    {
        "name": "Fire & Steel",
        "description": "Combination of aggressive creatures and powerful artifacts.",
    },
    {
        "name": "Nature's Wrath",
        "description": "Green ramp deck playing large creatures and overwhelming spells.",
    },
    {
        "name": "Darkness Rising",
        "description": "Black deck using sacrifice and dark rituals for powerful effects.",
    },
]

# Sample user data
USER_NAMES = [
    "Alex",
    "Blake",
    "Casey",
    "Drew",
    "Emery",
    "Finley",
    "Gray",
    "Harper",
    "Indigo",
    "Jordan",
    "Kai",
    "Logan",
    "Morgan",
    "Nova",
    "Oakley",
    "Parker",
    "Quinn",
    "River",
    "Sage",
    "Taylor",
    "Unique",
    "Val",
    "Winter",
    "Xander",
    "Yarrow",
    "Zara",
    "Avery",
    "Bay",
    "Carmen",
    "Dakota",
    "Eden",
    "Flynn",
]

ADJECTIVES = [
    "Swift",
    "Mighty",
    "Clever",
    "Bold",
    "Fierce",
    "Wise",
    "Noble",
    "Brave",
    "Cunning",
    "Radiant",
    "Shadow",
    "Storm",
    "Frost",
    "Flame",
    "Stone",
    "Wind",
    "Iron",
    "Silver",
    "Golden",
    "Crystal",
    "Mystic",
    "Ancient",
    "Elder",
    "Prime",
]


class DataGenerator:
    """Generator for creating realistic sample data."""

    def __init__(self):
        self.password_helper = PasswordHelper()
        self.created_users: List[User] = []
        self.created_cards: List[Card] = []
        self.created_decks: List[Deck] = []

    async def clear_existing_data(self):
        """Clear all existing data from the database."""
        print("🗑️  Clearing existing data...")

        # Delete in reverse dependency order
        await DeckCard.all().delete()
        await Deck.all().delete()
        await Card.all().delete()
        await User.all().delete()

        print("✅ Existing data cleared")

    async def generate_users(self, count: int = 10) -> List[User]:
        """Generate sample users with realistic data."""
        print(f"👥 Generating {count} users...")

        users = []
        used_usernames = set()
        used_emails = set()

        for i in range(count):
            # Generate unique username
            while True:
                adj = random.choice(ADJECTIVES)
                name = random.choice(USER_NAMES)
                username = f"{adj}{name}{random.randint(1, 999)}"
                if username not in used_usernames:
                    used_usernames.add(username)
                    break

            # Generate unique email
            while True:
                email = f"{username.lower()}@cardgame.example"
                if email not in used_emails:
                    used_emails.add(email)
                    break

            # Create user with hashed password
            password = f"password{random.randint(100, 999)}"
            hashed_password = self.password_helper.hash(password)

            user_data = {
                "id": uuid.uuid4(),
                "username": username,
                "email": email,
                "hashed_password": hashed_password,
                "name": f"{random.choice(ADJECTIVES)} {random.choice(USER_NAMES)}",
                "is_active": True,
                "is_verified": True,
                "is_superuser": i == 0,  # First user is admin
                "is_admin": i < 2,  # First two users are admins
            }

            user = await User.create(**user_data)
            users.append(user)

            if i < 2:
                print(f"📝 Admin user created: {username} / {email} / {password}")

        self.created_users = users
        print(f"✅ Created {len(users)} users")
        return users

    async def generate_cards(self, count: int = None) -> List[Card]:
        """Generate sample cards using predefined card data."""
        if count is None:
            count = len(SAMPLE_CARDS_DATA)

        print(f"🃏 Generating {count} cards...")

        cards = []
        card_pool = SAMPLE_CARDS_DATA.copy()

        # If we need more cards than in our sample data, generate variations
        if count > len(card_pool):
            base_cards = card_pool.copy()
            for i in range(count - len(card_pool)):
                base_card = random.choice(base_cards)
                variation_num = (i // len(base_cards)) + 2
                card_pool.append(
                    {
                        "name": f"{base_card['name']} {variation_num}",
                        "text": base_card["text"],
                    }
                )

        # Create cards
        for i in range(count):
            card_data = (
                card_pool[i] if i < len(card_pool) else random.choice(SAMPLE_CARDS_DATA)
            )

            card = await Card.create(name=card_data["name"], text=card_data["text"])
            cards.append(card)

        self.created_cards = cards
        print(f"✅ Created {len(cards)} cards")
        return cards

    async def generate_decks(self, count: int = 15) -> List[Deck]:
        """Generate sample decks with realistic themes."""
        if not self.created_users:
            raise ValueError("Users must be created before decks")

        print(f"🎴 Generating {count} decks...")

        decks = []
        deck_pool = DECK_THEMES.copy()

        # If we need more decks than themes, generate variations
        if count > len(deck_pool):
            base_themes = deck_pool.copy()
            for i in range(count - len(deck_pool)):
                base_theme = random.choice(base_themes)
                variation_num = (i // len(base_themes)) + 2
                deck_pool.append(
                    {
                        "name": f"{base_theme['name']} {variation_num}",
                        "description": f"{base_theme['description']} (Variant {variation_num})",
                    }
                )

        used_names = set()

        for i in range(count):
            theme = deck_pool[i] if i < len(deck_pool) else random.choice(DECK_THEMES)

            # Ensure unique name
            name = theme["name"]
            counter = 1
            while name in used_names:
                counter += 1
                name = f"{theme['name']} {counter}"
            used_names.add(name)

            # Assign random owner
            owner = random.choice(self.created_users)

            deck = await Deck.create(
                name=name,
                description=theme["description"],
                is_valid=random.choice([True, False]),
                owner=owner,
            )
            decks.append(deck)

        self.created_decks = decks
        print(f"✅ Created {len(decks)} decks")
        return decks

    async def generate_deck_cards(self) -> List[DeckCard]:
        """Generate deck-card relationships (which cards are in which decks)."""
        if not self.created_decks or not self.created_cards:
            raise ValueError(
                "Decks and cards must be created before deck-card relationships"
            )

        print("🔗 Generating deck-card relationships...")

        deck_cards = []

        for deck in self.created_decks:
            # Each deck gets 15-60 cards (realistic deck sizes)
            deck_size = random.randint(15, 60)

            # Select random cards for this deck
            selected_cards = random.sample(
                self.created_cards, min(deck_size, len(self.created_cards))
            )

            for card in selected_cards:
                # Most cards appear 1-4 times in a deck
                quantity = random.choices([1, 2, 3, 4], weights=[40, 30, 20, 10])[0]

                try:
                    deck_card = await DeckCard.create(
                        deck=deck, card=card, quantity=quantity
                    )
                    deck_cards.append(deck_card)
                except Exception as e:
                    # Skip if this combination already exists (unique constraint)
                    continue

        print(f"✅ Created {len(deck_cards)} deck-card relationships")
        return deck_cards

    async def generate_statistics(self):
        """Print statistics about the generated data."""
        print("\n📊 Database Statistics:")
        print(f"   Users: {await User.all().count()}")
        print(f"   Cards: {await Card.all().count()}")
        print(f"   Decks: {await Deck.all().count()}")
        print(f"   Deck-Card relations: {await DeckCard.all().count()}")

        # Sample data preview
        print("\n🔍 Sample Data Preview:")

        # Show first few users
        users = await User.all().limit(3)
        for user in users:
            print(f"   User: {user.username} ({user.email}) - Admin: {user.is_admin}")

        # Show first few cards
        cards = await Card.all().limit(3)
        for card in cards:
            print(f"   Card: {card.name} - {card.text[:50]}...")

        # Show first few decks with card counts
        decks = await Deck.all().prefetch_related("deck_cards").limit(3)
        for deck in decks:
            card_count = len(deck.deck_cards)
            print(
                f"   Deck: {deck.name} ({card_count} cards) - {deck.description[:50]}..."
            )


async def main():
    """Main function to generate database content."""
    parser = argparse.ArgumentParser(
        description="Generate dummy data for the card game database"
    )
    parser.add_argument(
        "--users", type=int, default=15, help="Number of users to create"
    )
    parser.add_argument(
        "--cards",
        type=int,
        default=None,
        help="Number of cards to create (default: all sample cards)",
    )
    parser.add_argument(
        "--decks", type=int, default=20, help="Number of decks to create"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing data before generating new data",
    )

    args = parser.parse_args()

    print("🚀 Starting database population...")
    print(f"Database URI: {settings.DATABASE_URI}")

    # Initialize database
    await init_db()

    try:
        generator = DataGenerator()
        # await generator.clear_existing_data()
        if args.clear:
            await generator.clear_existing_data()

        # Generate data in dependency order
        await generator.generate_users(args.users)
        await generator.generate_cards(args.cards)
        await generator.generate_decks(args.decks)
        await generator.generate_deck_cards()

        # Show statistics
        await generator.generate_statistics()

        print("\n🎉 Database population completed successfully!")

    except Exception as e:
        print(f"Error during data generation: {e}")
        raise
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
