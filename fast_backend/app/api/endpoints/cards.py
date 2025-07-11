from typing import List
from fastapi import APIRouter, HTTPException, status

from app.models.cards import Card as CardModel
from app.schemas.cards import CardCreate, CardUpdate, CardResponse

router = APIRouter()

@router.get("/", response_model=List[CardResponse])
async def get_cards():
    """Get all cards."""
    return await CardModel.all()

@router.get("/{card_id}", response_model=CardResponse)
async def get_card(card_id: int):
    """Get a specific card by ID."""
    card = await CardModel.get_or_none(id=card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Card with id: {card_id} not found",
        )
        
    return card

@router.post("/", response_model=CardResponse, status_code=status.HTTP_201_CREATED)
async def create_card(card: CardCreate):
    """Create a new card."""
    return await CardModel.create(**card.model_dump())

@router.put("/{card_id}", response_model=CardResponse)
async def update_card(card_id: int, data: CardUpdate):
    """Update an existing card."""
    # Extract only the set fields from the request
    card = await CardModel.get_or_none(id=card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Card with id: {card_id} not found",
        )
    update_data = data.model_dump(exclude_unset=True)
    
    # If no fields to update, just return the current card
    if not update_data:
        return card
    
    await card.update_from_dict(update_data).save()
    return card

@router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_card(card_id: int):
    """Delete a card."""
    card = await CardModel.get_or_none(id=card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Card with id: {card_id} not found",
        )
    await card.delete()
    return None #{"detail": "Card deleted successfully"}