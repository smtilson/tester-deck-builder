"""Test endpoints for verifying database connection."""

from fastapi import APIRouter, Depends, HTTPException
from typing import Any
from beanie import Document
from pydantic import Field


from fast_backend.app.models.decks import Deck
from fast_backend.app.models.cards import Card
from fast_backend.app.models.deck_cards import DeckCard

# prefix="/test", tags=["test"] should be passed to the below maybe
# but it looks like this is done in the routes file.
router = APIRouter(tags=["test"])


class TestDocument(Document):
    """A simple test document to verify database connection."""
    value: str

    class Settings:
        name = "test_documents"

@router.get("/db-connection")
async def test_db_connection():
    """Test that the database connection is working."""
    try:
        test_doc = TestDocument(value="Connection Successful.")
        await test_doc.insert()
        found_doc = await TestDocument.find_one(TestDocument.value == "Connection Successful.")
        if found_doc:
            await found_doc.delete()
            return {"message": "Database connection is working"}
        else:
            raise HTTPException(status_code=500, detail="Test document not found after insertion.")
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


