"""Test endpoints for verifying database connection."""

from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Any
from beanie import Document
from pydantic import Field


from fast_backend.app.models.decks import Deck
from fast_backend.app.models.cards import Card
from fast_backend.app.crud.cards import CardRepo
from fast_backend.app.schemas.cards import CardCreate, CardUpdate, CardResponse
from fast_backend.app.models.deck_cards import DeckCard
from fast_backend.app.models.test import TestDocument
from fast_backend.app.db.config_db import drop_db

# prefix="/test", tags=["test"] should be passed to the below maybe
# but it looks like this is done in the routes file.
router = APIRouter(tags=["test"])



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

@router.get("/add-test")
async def test_add_card(request: Request):
    try:
        await drop_db(client=request.app.state.db_client)
        msg = "Database dropped successfully"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error dropping database: {str(e)}")
    sample_data = {"name":"test card", "text":"This is a test card"}
    try:
        print("in try block")
        card_in = CardCreate(**sample_data)
        print("card_in schema created")
        card = await CardRepo.create_card(card_in=card_in)
        print("cardrepo method called")
        return {"earlier_message":msg,"message": "Card added successfully", "card": card}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding card: {str(e)}")

@router.get("/get_test")
async def test_get_card():
    try:
        cards = await CardRepo.get_all_cards()
        if cards:
            return {"message": "Cards retrieved successfully", "cards": cards}
        else:
            raise HTTPException(status_code=404, detail="No cards found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving card: {str(e)}")

@router.get("/drop-db")
async def test_drop_db(request: Request):
    try:
        client = request.app.state.db_client
        await drop_db(client=client)
        return {"message": "Database dropped successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error dropping database: {str(e)}")