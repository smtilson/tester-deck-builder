from fastapi import APIRouter, HTTPException, status

from fast_backend.app.models import DeckCard as DeckCardModel
from fast_backend.app.schemas import (
    DeckCardResponse,
    DeckCardCreate,
    DeckCardUpdate,
)
from fast_backend.app.models import Deck as DeckModel
from fast_backend.app.models import Card as CardModel
from fast_backend.app.crud.deck_cards import DeckCardManager as crud

router = APIRouter()


@router.post(
    "/{deck_id}/cards",
    response_model=DeckCardResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_card_to_deck(deck_id: int, card_data: DeckCardCreate):
    """Add a card to a deck."""
    deck = await DeckModel.get_or_none(id=deck_id)
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deck with ID {deck_id} not found",
        )

    card_db = await CardModel.get_or_none(id=card_data.card_id)
    if not card_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No card with ID in {card_data.card_id} was found.",
        )
    # Check if the card already exists in the deck
    existing_deck_card = await DeckCardModel.get_or_none(
        deck_id=deck_id, card_id=card_data.card_id
    )
    if existing_deck_card:
        existing_deck_card.quantity += card_data.quantity
        await existing_deck_card.save()
        return existing_deck_card
    else:
        # Create the deck card relation
        deck_card = await DeckCardModel.create(
            deck_id=deck_id, card_id=card_data.card_id, quantity=card_data.quantity
        )
        return deck_card


# perhaps this should return the deck with the updated quantities
@router.put("/{deck_id}/update_card/{card_id}", response_model=DeckCardResponse)
async def update_card_in_deck(deck_id: int, card_id: int, data: DeckCardUpdate):
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


@router.delete(
    "/{deck_id}/remove_card/{card_id}", status_code=status.HTTP_204_NO_CONTENT
)
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
