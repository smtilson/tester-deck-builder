"""
Generate Magic: The Gathering style cards for the database.

This script creates a comprehensive set of MTG-inspired cards with:
- Different card types (Creatures, Spells, Artifacts, Enchantments, Lands)
- Realistic card names and effects
- Balanced distribution across rarities and colors

Usage:
    python -m app.generate_mtg_cards
    python -m app.generate_mtg_cards --count 500
"""

import asyncio
import argparse
import random
from typing import List, Dict

from fast_backend.app.models.cards import Card
from fast_backend.app.db.config_db import init_db, close_db


# MTG-inspired card templates
MTG_CREATURES = [
    # White Creatures
    {
        "name": "Serra Angel",
        "text": "Flying, Vigilance. A legendary warrior from the heavens.",
    },
    {
        "name": "Knight of the White Orchid",
        "text": "First Strike. When Knight enters, search for a Plains.",
    },
    {"name": "Soldier of Fortune", "text": "Vigilance. Gets +1/+1 when attacking."},
    {"name": "Guardian of Faith", "text": "Defender, Protection from black."},
    {
        "name": "Pegasus Rider",
        "text": "Flying. Can't be blocked by creatures with power 3 or greater.",
    },
    # Blue Creatures
    {"name": "Azure Drake", "text": "Flying. When Azure Drake enters, draw a card."},
    {
        "name": "Merfolk Wizard",
        "text": "Tap: Counter target spell unless its controller pays 1.",
    },
    {
        "name": "Sea Serpent",
        "text": "Can't attack unless defending player controls an Island.",
    },
    {
        "name": "Phantom Warrior",
        "text": "Can't be blocked. Unblockable shadow creature.",
    },
    {"name": "Storm Elemental", "text": "Flying. Returns to hand at end of turn."},
    # Black Creatures
    {
        "name": "Vampire Nighthawk",
        "text": "Flying, Deathtouch, Lifelink. Master of the night.",
    },
    {
        "name": "Zombie Master",
        "text": "Other Zombies get +1/+1. Tap: Create a 2/2 Zombie token.",
    },
    {
        "name": "Dark Assassin",
        "text": "When Dark Assassin enters, destroy target creature.",
    },
    {
        "name": "Specter of Doom",
        "text": "Flying. When deals damage, opponent discards a card.",
    },
    {
        "name": "Bone Dragon",
        "text": "Flying. Can be cast from graveyard by exiling three creatures.",
    },
    # Red Creatures
    {
        "name": "Lightning Dragon",
        "text": "Flying, Haste. When attacks, deal 2 damage to any target.",
    },
    {"name": "Goblin King", "text": "Other Goblins get +1/+1 and Mountainwalk."},
    {
        "name": "Fire Elemental",
        "text": "When enters play, deal 3 damage to target creature or player.",
    },
    {
        "name": "Berserker Warrior",
        "text": "Haste, Trample. Must attack each turn if able.",
    },
    {
        "name": "Phoenix of Renewal",
        "text": "Flying. When dies, return to hand at end of turn.",
    },
    # Green Creatures
    {
        "name": "Ancient Treant",
        "text": "Trample, Reach. Gets +1/+1 for each Forest you control.",
    },
    {
        "name": "Elvish Warrior",
        "text": "Other Elves get +1/+1. Tap: Add one green mana.",
    },
    {
        "name": "Forest Guardian",
        "text": "Defender, Regenerate. Protects all lands from destruction.",
    },
    {
        "name": "Beast of the Wild",
        "text": "Trample. Can't be blocked by more than one creature.",
    },
    {
        "name": "Nature Spirit",
        "text": "When enters, search library for a basic land and put into play.",
    },
]

MTG_SPELLS = [
    # White Spells
    {
        "name": "Divine Intervention",
        "text": "Prevent all damage that would be dealt this turn.",
    },
    {"name": "Healing Light", "text": "Target player gains 7 life."},
    {
        "name": "Wrath of Heaven",
        "text": "Destroy all creatures. They can't be regenerated.",
    },
    {
        "name": "Blessing of Peace",
        "text": "Target creature gets +2/+2 and gains Protection from black.",
    },
    {
        "name": "Sacred Bond",
        "text": "Enchant creature. Enchanted creature gets +1/+1 and Lifelink.",
    },
    # Blue Spells
    {
        "name": "Time Spiral",
        "text": "Each player shuffles hand and graveyard into library, then draws 7 cards.",
    },
    {"name": "Counterspell", "text": "Counter target spell."},
    {"name": "Mind Probe", "text": "Look at target player's hand. Draw a card."},
    {"name": "Teleportation", "text": "Return target creature to its owner's hand."},
    {"name": "Arcane Intellect", "text": "Draw three cards."},
    # Black Spells
    {
        "name": "Death's Shadow",
        "text": "Destroy target non-artifact, non-black creature.",
    },
    {"name": "Dark Ritual", "text": "Add three black mana to your mana pool."},
    {"name": "Vampiric Drain", "text": "Target creature gets -2/-2. You gain 2 life."},
    {"name": "Raise Dead", "text": "Return target creature from graveyard to hand."},
    {"name": "Soul Burn", "text": "Deal X damage to target. You gain X life."},
    # Red Spells
    {"name": "Lightning Bolt", "text": "Deal 3 damage to any target."},
    {"name": "Fireball", "text": "Deal X damage divided among any number of targets."},
    {"name": "Meteor Strike", "text": "Deal 5 damage to target creature or player."},
    {"name": "Flame Wave", "text": "Deal 2 damage to each creature and player."},
    {
        "name": "Dragon's Breath",
        "text": "Deal 4 damage to target creature. If it dies, deal 2 damage to its controller.",
    },
    # Green Spells
    {"name": "Giant Growth", "text": "Target creature gets +3/+3 until end of turn."},
    {
        "name": "Nature's Blessing",
        "text": "Search library for up to two basic lands and put them into play.",
    },
    {
        "name": "Regeneration",
        "text": "Target creature gains Regenerate until end of turn.",
    },
    {
        "name": "Hurricane",
        "text": "Deal X damage to each creature with flying and each player.",
    },
    {
        "name": "Overrun",
        "text": "Creatures you control get +3/+3 and Trample until end of turn.",
    },
]

MTG_ARTIFACTS = [
    {"name": "Sol Ring", "text": "Tap: Add two colorless mana to your mana pool."},
    {
        "name": "Sword of Light",
        "text": "Equipped creature gets +2/+2 and Protection from black. Equip 2.",
    },
    {
        "name": "Crystal Ball",
        "text": "Tap, Pay 1: Scry 2 (Look at top 2 cards, put any on bottom).",
    },
    {
        "name": "Mana Vault",
        "text": "Tap: Add three colorless mana. Doesn't untap during untap step.",
    },
    {
        "name": "Ring of Power",
        "text": "Equipped creature gets +1/+1 for each artifact you control. Equip 3.",
    },
    {"name": "Staff of Wizardry", "text": "Spells you cast cost 1 less to cast."},
    {"name": "Shield Generator", "text": "Creatures you control get +0/+2."},
    {
        "name": "Time Bomb",
        "text": "At beginning of upkeep, put a charge counter. When reaches 4, deal 4 damage to each creature.",
    },
    {
        "name": "Golem Heart",
        "text": "Tap: Create a 2/2 colorless Golem artifact creature token.",
    },
    {
        "name": "Memory Jar",
        "text": "Tap, Sacrifice: Each player exiles hand and draws 7 cards. At end of turn, discard and return exiled cards.",
    },
]

MTG_ENCHANTMENTS = [
    {
        "name": "Circle of Protection",
        "text": "Pay 1: Prevent next 1 damage from a red source.",
    },
    {
        "name": "Mirari's Wake",
        "text": "Creatures you control get +1/+1. Lands produce an additional mana.",
    },
    {
        "name": "Necropotence",
        "text": "Skip draw step. Pay 1 life: Exile top card of library. Put into hand at end of turn.",
    },
    {
        "name": "Sulfuric Vortex",
        "text": "At beginning of each end step, deal 2 damage to each player.",
    },
    {
        "name": "Wild Growth",
        "text": "Enchant land. Enchanted land produces an additional green mana.",
    },
    {
        "name": "Cursed Land",
        "text": "All lands are Swamps in addition to their other types.",
    },
    {
        "name": "Sacred Mesa",
        "text": "At beginning of upkeep, sacrifice unless you pay 2. Pay 2: Create 1/1 Pegasus token with flying.",
    },
    {
        "name": "Rhystic Study",
        "text": "Whenever opponent casts spell, you may draw a card unless they pay 1.",
    },
    {
        "name": "Pandemonium",
        "text": "Whenever a creature enters play, it deals damage equal to its power to target creature or player.",
    },
    {"name": "Glorious Anthem", "text": "Creatures you control get +1/+1."},
]

MTG_LANDS = [
    {"name": "Plains", "text": "Tap: Add one white mana to your mana pool."},
    {"name": "Island", "text": "Tap: Add one blue mana to your mana pool."},
    {"name": "Swamp", "text": "Tap: Add one black mana to your mana pool."},
    {"name": "Mountain", "text": "Tap: Add one red mana to your mana pool."},
    {"name": "Forest", "text": "Tap: Add one green mana to your mana pool."},
    {
        "name": "Volcanic Island",
        "text": "Tap: Add blue or red mana. Counts as Island and Mountain.",
    },
    {
        "name": "Underground Sea",
        "text": "Tap: Add blue or black mana. Counts as Island and Swamp.",
    },
    {
        "name": "Tropical Island",
        "text": "Tap: Add blue or green mana. Counts as Island and Forest.",
    },
    {
        "name": "Savannah",
        "text": "Tap: Add green or white mana. Counts as Forest and Plains.",
    },
    {
        "name": "Scrubland",
        "text": "Tap: Add white or black mana. Counts as Plains and Swamp.",
    },
    {
        "name": "Ancient Library",
        "text": "Tap: Add 1 colorless mana. Pay 2, Tap: Draw a card.",
    },
    {
        "name": "Mishra's Workshop",
        "text": "Tap: Add 3 colorless mana. Use only to cast artifact spells.",
    },
    {
        "name": "City of Brass",
        "text": "Tap: Add one mana of any color. Deal 1 damage to you.",
    },
    {
        "name": "Gemstone Mine",
        "text": "Tap, Remove counter: Add mana of any color. Enters with 3 counters.",
    },
    {
        "name": "Wasteland",
        "text": "Tap: Add 1 colorless. Tap, Sacrifice: Destroy target non-basic land.",
    },
]

# Prefixes and suffixes for generating unique names
PREFIXES = [
    "Ancient",
    "Mystic",
    "Sacred",
    "Dark",
    "Bright",
    "Shadow",
    "Storm",
    "Fire",
    "Ice",
    "Earth",
    "Celestial",
    "Infernal",
    "Divine",
    "Cursed",
    "Blessed",
    "Forgotten",
    "Lost",
    "Hidden",
    "Royal",
    "Noble",
    "Mighty",
    "Weak",
    "Strong",
    "Swift",
    "Slow",
    "Wise",
    "Foolish",
    "Brave",
    "Coward",
    "Lucky",
]

SUFFIXES = [
    "of Power",
    "of Wisdom",
    "of Strength",
    "of Speed",
    "of Magic",
    "of Light",
    "of Darkness",
    "of the Void",
    "of the Storm",
    "of the Forest",
    "of the Sea",
    "of the Mountain",
    "of the Plains",
    "the Magnificent",
    "the Terrible",
    "the Wise",
    "the Brave",
    "the Swift",
    "the Mighty",
    "the Ancient",
    "the Eternal",
    "the Forgotten",
    "the Lost",
    "the Hidden",
    "the Sacred",
]


class MTGCardGenerator:
    """Generator for MTG-style cards."""

    def __init__(self):
        self.used_names = set()

    def generate_unique_name(self, base_cards: List[Dict]) -> str:
        """Generate a unique card name."""
        attempts = 0
        while attempts < 100:  # Prevent infinite loop
            if random.choice([True, False]) and attempts < 50:
                # Use base card name
                card = random.choice(base_cards)
                name = card["name"]
            else:
                # Generate new name
                base = random.choice(base_cards)["name"].split()[0]
                if random.choice([True, False]):
                    name = f"{random.choice(PREFIXES)} {base}"
                else:
                    name = f"{base} {random.choice(SUFFIXES)}"

            if name not in self.used_names:
                self.used_names.add(name)
                return name

            attempts += 1

        # Fallback with number
        base = random.choice(base_cards)["name"]
        counter = 1
        while f"{base} {counter}" in self.used_names:
            counter += 1
        name = f"{base} {counter}"
        self.used_names.add(name)
        return name

    async def generate_cards(self, count: int = 200) -> List[Card]:
        """Generate a specified number of MTG-style cards."""
        print(f"🃏 Generating {count} MTG-style cards...")

        # Card type distribution
        creature_ratio = 0.4
        spell_ratio = 0.3
        artifact_ratio = 0.15
        enchantment_ratio = 0.1
        land_ratio = 0.05

        creatures_count = int(count * creature_ratio)
        spells_count = int(count * spell_ratio)
        artifacts_count = int(count * artifact_ratio)
        enchantments_count = int(count * enchantment_ratio)
        lands_count = count - (
            creatures_count + spells_count + artifacts_count + enchantments_count
        )

        cards = []

        # Generate creatures
        for i in range(creatures_count):
            base_card = random.choice(MTG_CREATURES)
            name = self.generate_unique_name(MTG_CREATURES)
            card = await Card.create(name=name, text=base_card["text"])
            cards.append(card)

        # Generate spells
        for i in range(spells_count):
            base_card = random.choice(MTG_SPELLS)
            name = self.generate_unique_name(MTG_SPELLS)
            card = await Card.create(name=name, text=base_card["text"])
            cards.append(card)

        # Generate artifacts
        for i in range(artifacts_count):
            base_card = random.choice(MTG_ARTIFACTS)
            name = self.generate_unique_name(MTG_ARTIFACTS)
            card = await Card.create(name=name, text=base_card["text"])
            cards.append(card)

        # Generate enchantments
        for i in range(enchantments_count):
            base_card = random.choice(MTG_ENCHANTMENTS)
            name = self.generate_unique_name(MTG_ENCHANTMENTS)
            card = await Card.create(name=name, text=base_card["text"])
            cards.append(card)

        # Generate lands
        for i in range(lands_count):
            base_card = random.choice(MTG_LANDS)
            name = self.generate_unique_name(MTG_LANDS)
            card = await Card.create(name=name, text=base_card["text"])
            cards.append(card)

        print(f"✅ Generated {len(cards)} MTG-style cards:")
        print(f"   Creatures: {creatures_count}")
        print(f"   Spells: {spells_count}")
        print(f"   Artifacts: {artifacts_count}")
        print(f"   Enchantments: {enchantments_count}")
        print(f"   Lands: {lands_count}")

        return cards


async def main():
    """Main function to generate MTG-style cards."""
    parser = argparse.ArgumentParser(description="Generate MTG-style cards")
    parser.add_argument(
        "--count", type=int, default=200, help="Number of cards to generate"
    )
    parser.add_argument(
        "--clear", action="store_true", help="Clear existing cards first"
    )

    args = parser.parse_args()

    print("🚀 Starting MTG card generation...")

    await init_db()

    try:
        if args.clear:
            print("🗑️  Clearing existing cards...")
            await Card.all().delete()

        generator = MTGCardGenerator()
        cards = await generator.generate_cards(args.count)

        print(f"\n🎉 Successfully generated {len(cards)} MTG-style cards!")

    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
