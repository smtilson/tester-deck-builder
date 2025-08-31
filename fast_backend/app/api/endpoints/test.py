"""Test endpoints for verifying database connection."""

from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Any
from beanie import Document
from pydantic import Field


from fast_backend.app.models import Deck
from fast_backend.app.models import Card
from fast_backend.app.crud.cards import CardManager
from fast_backend.app.schemas import CardCreate, CardUpdate, CardResponse
from fast_backend.app.models import DeckCard
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
        found_doc = await TestDocument.find_one(
            TestDocument.value == "Connection Successful."
        )
        if found_doc:
            await found_doc.delete()
            return {"message": "Database connection is working"}
        else:
            raise HTTPException(
                status_code=500, detail="Test document not found after insertion."
            )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Database connection error: {str(e)}"
        )


@router.get("/")
async def test_route():
    return {"message": "Test route"}