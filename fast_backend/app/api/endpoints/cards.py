from typing import List
from fastapi import APIRouter, HTTPException, status
from tortoise.exceptions import DoesNotExist

from app.api.models.cards import Card as CardModel
from app.api.schemas.cards import Card, CardCreate, CardUpdate

router = APIRouter()

@router.get("/", response_model=List[Card])
async def get_cards():
    """Get all cards."""
    return await Card.from_queryset(CardModel.all())

@router.get("/{card_id}", response_model=Card)
async def get_card(card_id: int):
    """Get a specific card by ID."""
    try:
        return await Card.from_queryset_single(CardModel.get(id=card_id))
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Card with id: {card_id} not found",
        )

@router.post("/", response_model=Card, status_code=status.HTTP_201_CREATED)
async def create_card(card: CardCreate):
    """Create a new card."""
    card_obj = await CardModel.create(**card.dict(exclude_unset=True))
    return await Card.from_tortoise_orm(card_obj)

@router.put("/{card_id}", response_model=Card)
async def update_card(card_id: int, card: CardUpdate):
    """Update an existing card."""
    # Extract only the set fields from the request
    update_data = card.dict(exclude_unset=True)
    
    # If no fields to update, just return the current card
    if not update_data:
        try:
            return await Card.from_queryset_single(CardModel.get(id=card_id))
        except DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Card with id: {card_id} not found",
            )
    
    # Check if the card exists
    try:
        await CardModel.get(id=card_id)
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Card with id: {card_id} not found",
        )
    
    # Update the card
    await CardModel.filter(id=card_id).update(**update_data)
    
    # Return the updated card
    return await Card.from_queryset_single(CardModel.get(id=card_id))

@router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_card(card_id: int):
    """Delete a card."""
    deleted_count = await CardModel.filter(id=card_id).delete()
    if not deleted_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Card with id: {card_id} not found",
        )
    return {"detail": "Card deleted successfully"}
