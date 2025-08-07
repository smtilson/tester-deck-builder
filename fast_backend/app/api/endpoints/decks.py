from fastapi import APIRouter, HTTPException, status

from ...crud import decks as crud
from ...schemas.decks import (
    DeckResponse,
    DeckCreate,
    DeckUpdate,
    DeckResponseWithCards,
)

router = APIRouter()


@router.get("/", response_model=list[DeckResponse])
async def get_decks():
    """Get all decks."""
    return await crud.get_all_decks()


@router.get("/{deck_id}", response_model=DeckResponse)
async def get_deck(deck_id: int):
    """Get a specific deck by ID."""
    deck = await crud.get_deck(deck_id=deck_id)
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deck with ID {deck_id} not found",
        )
    return deck


@router.post("/", response_model=DeckResponse, status_code=status.HTTP_201_CREATED)
async def create_deck(deck: DeckCreate):
    """Create a new deck."""
    return await crud.create_deck_record(deck_data=deck)


@router.put("/{deck_id}", response_model=DeckResponse)
async def update_deck(deck_id: int, data: DeckUpdate):
    """Update an existing deck."""
    deck = await crud.update_deck(deck_id=deck_id, deck_data=data)
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deck with ID {deck_id} not found",
        )
    return deck


@router.delete("/{deck_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deck(deck_id: int):
    """Delete a deck."""
    deleted_successfully = await crud.delete_deck(deck_id=deck_id)
    if not deleted_successfully:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deck with ID {deck_id} not found",
        )
    return None
