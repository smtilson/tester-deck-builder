from fastapi import APIRouter, HTTPException, status

from ...schemas.cards import CardCreate, CardUpdate, CardResponse
from ...crud.cards import CardRepo as crud  # Import the crud module

router = APIRouter()


@router.get("/", response_model=list[CardResponse])
async def get_cards():
    """Get all cards."""
    return await crud.get_all_cards()


@router.get("/{card_id}", response_model=CardResponse)
async def get_card(card_id: int):
    """Get a specific card by ID."""
    card = await crud.get_card(card_id=card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Card with id: {card_id} not found",
        )
    return card


@router.post("/", response_model=CardResponse, status_code=status.HTTP_201_CREATED)
async def create_card(card: CardCreate):
    """Create a new card."""
    return await crud.create_card(card_data=card)


@router.put("/{card_id}", response_model=CardResponse)
async def update_card(card_id: int, data: CardUpdate):
    """Update an existing card."""
    card = await crud.update_card(card_id=card_id, card_data=data)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Card with id: {card_id} not found",
        )
    return card


@router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_card(card_id: int):
    """Delete a card."""
    deleted_successfully = await crud.delete_card(card_id=card_id)
    if not deleted_successfully:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Card with id: {card_id} not found",
        )
    return None
