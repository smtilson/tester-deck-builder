from typing import List, Optional
from app.models.cards import Card as CardModel
from app.schemas.cards import CardCreate, CardUpdate

async def create_card(card_data: CardCreate) -> CardModel:
    """
    Create a card.
    
    Args:
        card_data: The card data from the request
        
    Returns:
        The created card as a Pydantic model
    """
    return await CardModel.create(**card_data.dict())

async def get_card(card_id: int) -> Optional[CardModel]:
    """
    Get a card by its ID.
    
    Args:
        card_id: The ID of the card to retrieve
        
    Returns:
        The card as a Pydantic model, or None if it doesn't exist
    """
    return await CardModel.get_or_none(id=card_id)

async def get_all_cards() -> List[CardModel]:
    """
    Get all cards.
    
    Returns:
        A list of all cards as Pydantic models
    """
    return await CardModel.all()

async def update_card(card_id: int, card_data: CardUpdate) -> Optional[CardModel]:
    """
    Update a card.
    
    Args:
        card_id: The ID of the card to update
        card_data: The updated card data from the request
        
    Returns:
        The updated card as a Pydantic model, or None if the card doesn't exist
    """
    card_obj = await CardModel.get_or_none(id=card_id)
    if card_obj:
        await card_obj.update_from_dict(card_data.dict())
        await card_obj.save()
    return card_obj

async def delete_card(card_id: int) -> bool:
    """
    Delete a card.
    
    Args:
        card_id: The ID of the card to delete
        
    Returns:
        True if the card was deleted, False if it doesn't exist
    """
    card_obj = await CardModel.get_or_none(id=card_id)
    if card_obj:
        await card_obj.delete()
        return True
    return False
