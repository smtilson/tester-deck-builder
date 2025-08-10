"""Test endpoints for verifying database connection."""

from fastapi import APIRouter, Depends, HTTPException
from typing import Any

from fast_backend.app.models.decks import Deck
from fast_backend.app.models.cards import Card
from fast_backend.app.models.deck_cards import DeckCard

# prefix="/test", tags=["test"] should be passed to the below maybe
# but it looks like this is done in the routes file.
router = APIRouter()


@router.get("/db-connection")
async def test_db_connection():
    """Test that the database connection is working."""
    try:
        # Try to count decks
        deck_count = await Deck.all().count()
        # Try to count cards
        card_count = await Card.all().count()
        deck_card_count = await DeckCard.all().count()

        return {
            "status": "success",
            "message": "Database connection is working",
            "data": {
                "deck_count": deck_count,
                "card_count": card_count,
                "deck_card_count": deck_card_count,
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Database connection error: {str(e)}"
        )


@router.get("/")
async def test_route():
    return {"message": "Test route"}


@router.get("/decks")
async def test_get_decks() -> list[dict[str, Any]]:
    """Get all decks with their cards to test relationships."""
    try:
        decks = await Deck.all().prefetch_related("deck_cards__card")

        result = []
        for deck in decks:
            deck_data = {
                "id": deck.id,
                "name": deck.name,
                "description": deck.description,
                "cards": [],
            }

            # Get all cards in this deck
            deck_cards = await deck.deck_cards.all()
            for deck_card in deck_cards:
                card = await deck_card.card
                deck_data["cards"].append(
                    {"id": card.id, "name": card.name, "quantity": deck_card.quantity}
                )

            result.append(deck_data)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving decks: {str(e)}")
