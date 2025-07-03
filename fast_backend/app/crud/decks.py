from typing import List, Optional
from app.models.cards import Card as CardModel
from app.models.decks import Deck as DeckModel, DeckCard as DeckCardModel
from app.schemas.decks import DeckCreate, DeckUpdate

async def create_deck_record(deck_data: DeckCreate) -> DeckModel:
    """
    Create a deck.
    
    Args:
        deck_data: The deck data from the request
        
    Returns:
        The created deck as a Pydantic model
    """
    deck_data_dict = deck_data.dict(exclude={'cards'})
    deck_obj = await DeckModel.create(**deck_data_dict, owner_id=1)
    # Always fetch owner relations if the returned object needs it right away for further processing
    # or for consistent return type for the caller.
    # await deck_obj.fetch_related("owner") 
    return deck_obj
    
async def get_deck(deck_id: int) -> Optional[DeckModel]:
    """
    Get a deck by its ID.
    
    Args:
        deck_id: The ID of the deck to retrieve
        
    Returns:
        The deck as a Pydantic model, or None if it doesn't exist
    """
    # prefetch owner as well once users are implemented
    return await DeckModel.get_or_none(id=deck_id).prefetch_related("deck_cards__card")

async def get_all_decks() -> List[DeckModel]:
    """
    Get all decks.
    
    Returns:
        A list of all decks as Pydantic models
    """
    # prefetch owner as well once users are implemented
    decks = await DeckModel.all().prefetch_related("deck_cards__card")
    return decks

async def update_deck(deck_id: int, deck_data: DeckUpdate) -> Optional[DeckModel]:
    """
    Update a deck.
    
    Args:
        deck_id: The ID of the deck to update
        deck_data: The updated deck data from the request
        
    Returns:
        The updated deck as a Pydantic model, or None if the deck doesn't exist
    """
    deck_obj = await DeckModel.get_or_none(id=deck_id)
    if deck_obj:
        await deck_obj.update_from_dict(deck_data.dict()).save()
    return deck_obj

async def delete_deck(deck_id: int) -> bool:
    """
    Delete a deck.
    
    Args:
        deck_id: The ID of the deck to delete
        
    Returns:
        True if the deck was deleted, False if it doesn't exist
    """
    deck_obj = await DeckModel.get_or_none(id=deck_id)
    if deck_obj:
        await deck_obj.delete()
        return True
    return False
