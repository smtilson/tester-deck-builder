#!/usr/bin/env python
"""Script to add sample data to the database."""
import asyncio
import sys
import os
import traceback

# Add the parent directory to the path so we can import our app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models.cards import Card
from app.models.decks import Deck
from app.models.deck_cards import DeckCard
from app.api.db.config import init_db, close_db
from tortoise import Tortoise

async def add_sample_data():
    """Add sample data to the database."""
    # Initialize the database connection
    await init_db()

    try:
        # Create a sample card
        card = await Card.create(
            name="Sample Card",
            text="This is a sample card for testing",
        )
        print(f"Created card: {card.name} (ID: {card.id})")

        # Create a sample deck
        deck = await Deck.create(
            name="Sample Deck",
            description="This is a sample deck for testing",
            owner_id=1,  # Placeholder owner ID
        )
        print(f"Created deck: {deck.name} (ID: {deck.id})")

        # Add the card to the deck
        deck_card = await DeckCard.create(deck=deck, card=card, quantity=2)
        print(f"Added {deck_card.quantity}x card {card.id} to deck {deck.id}")

        # Verify we can retrieve the data
        retrieved_deck = await Deck.get(id=deck.id).prefetch_related("deck_cards__card")
        print(f"Retrieved deck: {retrieved_deck.name}")

        deck_cards = await retrieved_deck.deck_cards.all()
        for dc in deck_cards:
            card = await dc.card
            print(f"Deck contains {dc.quantity}x {card.name}")

        return True
    except Exception as e:
        print(f"Error adding sample data: {e}")
        traceback.print_exc()  # Print the full traceback for debugging
        return False
    finally:
        # Close the database connection
        await close_db()


async def display_db():
    """Display all data in the database in a structured format."""
    await init_db()
    try:
        print("\n=== DATABASE CONTENTS ===\n")
        
        # Get all cards
        cards = await Card.all()
        print(f"Total cards: {len(cards)}")
        for card in cards:
            print(f"Card ID: {card.id}, Name: {card.name}, Text: {card.text}")
        
        print("\n---\n")
        
        # Get all decks
        decks = await Deck.all()
        print(f"Total decks: {len(decks)}")
        
        for deck in decks:
            print(f"\nDeck ID: {deck.id}, Name: {deck.name}")
            print(f"Description: {deck.description}")
            print(f"Owner ID: {deck.owner_id}, Valid: {deck.is_valid}")
            
            # Get deck cards for this deck
            deck_cards = await DeckCard.filter(deck_id=deck.id).prefetch_related("card")
            if not deck_cards:
                print("  This deck contains no cards.")
            else:
                print("  Cards in this deck:")
                for dc in deck_cards:
                    card = dc.card
                    print(f"    - {dc.quantity}x {card.name} (ID: {card.id})")
        
        # Get all deck_cards to show the relationships
        print("\n---\n")
        deck_cards = await DeckCard.all().prefetch_related("deck", "card")
        print(f"Total deck-card relationships: {len(deck_cards)}")
        for dc in deck_cards:
            deck = await dc.deck
            card = await dc.card
            print(f"Relationship ID: {dc.id}, Deck: {deck.name}, Card: {card.name}, Quantity: {dc.quantity}")
        
        print("\n=== END OF DATABASE CONTENTS ===\n")
        return True
    except Exception as e:
        print(f"Error displaying database: {e}")
        traceback.print_exc()  # Print the full traceback for debugging
        return False
    finally:
        # Close the database connection
        await close_db()


async def flush():
    """Flush the database by dropping all tables."""
    await init_db()
    try:
        print("Flushing database...")
        # Use the internal method to drop all databases
        
        # This is a more direct way to drop all tables
        await Tortoise._drop_databases()
        
        print("Database has been flushed successfully!")
        return True
    except Exception as e:
        print(f"Error flushing database: {e}")
        traceback.print_exc()  # Print the full traceback for debugging
        return False
    finally:
        # Close the database connection
        await close_db()


if __name__ == "__main__":
    
    success = asyncio.run(add_sample_data())
    if success:
        print("Sample data added successfully!")
    else:
        print("Failed to add sample data.")
        sys.exit(1)
    
    view = asyncio.run(display_db())
    if view:
        print("Sample data displayed successfully!")
    else:
        print("Failed to display sample data.")
        sys.exit(1)
