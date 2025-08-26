"""
Database utility functions for development and testing.

This script provides common database operations:
- Clear all data
- Show database statistics
- Export/import data
- Reset database to clean state

Usage:
    python -m app.db_utils --stats
    python -m app.db_utils --clear
    python -m app.db_utils --reset
"""

import asyncio
import argparse
import json
from datetime import datetime
from typing import Dict, Any, List

'''

from fast_backend.app.models import User
from fast_backend.app.models import Card
from fast_backend.app.models import Deck
from fast_backend.app.models import DeckCard
from fast_backend.app.db.config_db import init_db, close_db


class DatabaseUtils:
    """Utility class for database operations."""

    async def clear_all_data(self):
        """Clear all data from the database."""
        print("🗑️  Clearing all database data...")

        # Delete in dependency order
        deleted_deck_cards = await DeckCard.all().count()
        await DeckCard.all().delete()

        deleted_decks = await Deck.all().count()
        await Deck.all().delete()

        deleted_cards = await Card.all().count()
        await Card.all().delete()

        deleted_users = await User.all().count()
        await User.all().delete()

        print(f"✅ Cleared data:")
        print(f"   Deck-Cards: {deleted_deck_cards}")
        print(f"   Decks: {deleted_decks}")
        print(f"   Cards: {deleted_cards}")
        print(f"   Users: {deleted_users}")

    async def show_stats(self):
        """Show detailed database statistics."""
        print("📊 Database Statistics")
        print("=" * 50)

        # Basic counts
        user_count = await User.all().count()
        card_count = await Card.all().count()
        deck_count = await Deck.all().count()
        deck_card_count = await DeckCard.all().count()

        print(f"Total Records:")
        print(f"  Users: {user_count}")
        print(f"  Cards: {card_count}")
        print(f"  Decks: {deck_count}")
        print(f"  Deck-Card Relations: {deck_card_count}")
        print()

        # User breakdown
        if user_count > 0:
            admin_count = await User.filter(is_admin=True).count()
            verified_count = await User.filter(is_verified=True).count()
            active_count = await User.filter(is_active=True).count()

            print(f"User Breakdown:")
            print(f"  Admins: {admin_count}")
            print(f"  Verified: {verified_count}")
            print(f"  Active: {active_count}")
            print()

        # Deck breakdown
        if deck_count > 0:
            valid_decks = await Deck.filter(is_valid=True).count()
            print(f"Deck Breakdown:")
            print(f"  Valid Decks: {valid_decks}")
            print(f"  Invalid Decks: {deck_count - valid_decks}")

            # Average cards per deck
            if deck_card_count > 0:
                avg_cards = deck_card_count / deck_count
                print(f"  Average Cards per Deck: {avg_cards:.1f}")
            print()

        # Recent data
        print("Recent Data (Last 5):")

        # Recent users
        recent_users = await User.all().order_by("-created_at").limit(5)
        if recent_users:
            print("  Recent Users:")
            for user in recent_users:
                created = user.created_at.strftime("%Y-%m-%d %H:%M")
                print(f"    {user.username} ({user.email}) - {created}")

        # Recent cards
        recent_cards = await Card.all().order_by("-created_at").limit(5)
        if recent_cards:
            print("  Recent Cards:")
            for card in recent_cards:
                created = card.created_at.strftime("%Y-%m-%d %H:%M")
                print(f"    {card.name} - {created}")

        # Recent decks
        recent_decks = await Deck.all().order_by("-created_at").limit(5)
        if recent_decks:
            print("  Recent Decks:")
            for deck in recent_decks:
                created = deck.created_at.strftime("%Y-%m-%d %H:%M")
                print(f"    {deck.name} (Owner: {deck.owner_id}) - {created}")

    async def export_data(self, filename: str = None):
        """Export database data to JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"db_export_{timestamp}.json"

        print(f"📤 Exporting data to {filename}...")

        # Export all data
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "users": [],
            "cards": [],
            "decks": [],
            "deck_cards": [],
        }

        # Export users (excluding sensitive data)
        users = await User.all()
        for user in users:
            export_data["users"].append(
                {
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "name": user.name,
                    "is_active": user.is_active,
                    "is_verified": user.is_verified,
                    "is_admin": user.is_admin,
                    "created_at": user.created_at.isoformat(),
                }
            )

        # Export cards
        cards = await Card.all()
        for card in cards:
            export_data["cards"].append(
                {
                    "id": card.id,
                    "name": card.name,
                    "text": card.text,
                    "created_at": card.created_at.isoformat(),
                }
            )

        # Export decks
        decks = await Deck.all()
        for deck in decks:
            export_data["decks"].append(
                {
                    "id": deck.id,
                    "name": deck.name,
                    "description": deck.description,
                    "is_valid": deck.is_valid,
                    # blech
                    "owner_id": deck.owner.id if deck.owner else None,
                    "created_at": deck.created_at.isoformat(),
                }
            )

        # Export deck-card relationships
        deck_cards = await DeckCard.all().prefetch_related("deck", "card")
        for dc in deck_cards:
            export_data["deck_cards"].append(
                {
                    "id": dc.id,
                    "deck_id": dc.deck.id,
                    "card_id": dc.card.id,
                    "quantity": dc.quantity,
                    "created_at": dc.created_at.isoformat(),
                }
            )

        # Write to file
        with open(filename, "w") as f:
            json.dump(export_data, f, indent=2)

        print(
            f"✅ Exported {len(export_data['users'])} users, {len(export_data['cards'])} cards, {len(export_data['decks'])} decks"
        )

    async def show_sample_data(self):
        """Show sample of actual data in the database."""
        print("🔍 Sample Data")
        print("=" * 50)

        # Sample users
        users = await User.all().limit(3)
        if users:
            print("Sample Users:")
            for user in users:
                print(f"  {user.username} ({user.email})")
                print(f"    Admin: {user.is_admin}, Active: {user.is_active}")
            print()

        # Sample cards
        cards = await Card.all().limit(5)
        if cards:
            print("Sample Cards:")
            for card in cards:
                text_preview = (
                    card.text[:60] + "..." if len(card.text) > 60 else card.text
                )
                print(f"  {card.name}")
                print(f"    {text_preview}")
            print()

        # Sample decks with card counts
        decks = await Deck.all().prefetch_related("deck_cards").limit(3)
        if decks:
            print("Sample Decks:")
            for deck in decks:
                card_count = len(deck.deck_cards)
                desc_preview = (
                    deck.description[:50] + "..."
                    if len(deck.description) > 50
                    else deck.description
                )
                print(f"  {deck.name} ({card_count} cards)")
                print(f"    {desc_preview}")
                # blech
                print(f"    Owner ID: {deck.owner_id}, Valid: {deck.is_valid}")
            print()

    async def reset_database(self):
        """Reset database to clean state and run quick population."""
        print("🔄 Resetting database...")

        await self.clear_all_data()

        # Import and run quick populate
        try:
            from fast_backend.app.quick_populate import quick_populate

            print("🚀 Running quick population...")
            await quick_populate()
        except ImportError:
            print(
                "⚠️  quick_populate not available, database cleared but not repopulated"
            )


async def main():
    """Main function for database utilities."""
    parser = argparse.ArgumentParser(description="Database utility functions")
    parser.add_argument("--stats", action="store_true", help="Show database statistics")
    parser.add_argument("--clear", action="store_true", help="Clear all data")
    parser.add_argument(
        "--export", type=str, nargs="?", const="auto", help="Export data to JSON file"
    )
    parser.add_argument("--sample", action="store_true", help="Show sample data")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset database and populate with test data",
    )

    args = parser.parse_args()

    if not any([args.stats, args.clear, args.export, args.sample, args.reset]):
        parser.print_help()
        return

    await init_db()

    try:
        utils = DatabaseUtils()

        if args.stats:
            await utils.show_stats()

        if args.sample:
            await utils.show_sample_data()

        if args.export:
            filename = None if args.export == "auto" else args.export
            await utils.export_data(filename)

        if args.clear:
            await utils.clear_all_data()

        if args.reset:
            await utils.reset_database()

    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
'''
