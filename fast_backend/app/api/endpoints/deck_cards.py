from typing import List
from fastapi import APIRouter, HTTPException, status

from app.models.deck_cards import DeckCard as DeckCardModel
from app.schemas.deck_cards import DeckCardResponse, DeckCardCreate, DeckCardUpdate
from app.models.decks import Deck as DeckModel
from app.models.cards import Card as CardModel

router = APIRouter()

@router.post("/{deck_id}/cards", response_model=DeckCardResponse, status_code=status.HTTP_201_CREATED)
async def add_card_to_deck(deck_id: int, cards_to_add: List[DeckCardCreate]):
    """Add a card to a deck."""
    deck_ids = list({card.deck_id for card in cards_to_add})
    if len(deck_ids) != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can only add cards to one deck at a time.",
        )
    deck_id = deck_ids[0]
    deck = await DeckModel.get_or_none(id=deck_id)
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deck with ID {deck_id} not found",
        )
    
    cards_data = [(card.card_id, card.quantity) for card in cards_to_add]
    cards = await CardModel.filter(id__in=[card[0] for card in cards_data])
    if not cards:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Card with ID {card_to_add.card_id} not found",
        )
    # Check if the card already exists in the deck
    existing_deck_card = await DeckCardModel.get_or_none(deck_id=deck_id, card_id=card_to_add.card_id)
    if existing_deck_card:
        existing_deck_card.quantity += card_to_add.quantity
        await existing_deck_card.save()
        return existing_deck_card
    else:
        # Create the deck card relation
        deck_card = await DeckCardModel.create(deck_id=deck_id, card_id=card_to_add.card_id, quantity=card_to_add.quantity)
        return deck_card


# perhaps this should return the deck with the updated quantities
@router.put("/{deck_id}/update_card/{card_id}", response_model=DeckCardResponse)
async def update_card_in_deck(deck_id: int, card_id: int, data:
DeckCardUpdate):
    """Update a card in a deck."""
    deck_card = await DeckCardModel.get_or_none(deck_id=deck_id, card_id=card_id)
    if not deck_card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Card with ID {card_id} not found in deck {deck_id}",
        )
    
    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        return deck_card
    
    await deck_card.update_from_dict(update_data).save()
    return deck_card   

@router.delete("/{deck_id}/remove_card/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_card_from_deck(deck_id: int, card_id: int):
    """Remove a card from a deck."""
    deck_card = await DeckCardModel.get_or_none(deck_id=deck_id, card_id=card_id)
    if not deck_card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Card with ID {card_id} not found in deck {deck_id}",
        )
    await deck_card.delete()
    return None