from typing import List
from fastapi import APIRouter, HTTPException, status
from tortoise.exceptions import DoesNotExist
from tortoise.transactions import atomic

from app.models.decks import Deck as DeckModel
from app.models.deck_cards import DeckCard as DeckCardModel
from app.schemas.deck_cards import CardInDeckResponse
from app.schemas.decks import DeckResponse, DeckCreate, DeckUpdate, DeckResponseWithCards

router = APIRouter()


@router.get("/", response_model=List[DeckResponse])
async def get_decks():
    return await DeckModel.all()


@router.get("/{deck_id}", response_model=DeckResponse)
async def get_deck(deck_id: int):
    deck = await DeckModel.get_or_none(id=deck_id)
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deck with ID {deck_id} not found",
        )
    return deck


@router.post("/", response_model=DeckResponse, status_code=status.HTTP_201_CREATED)
@atomic()
async def create_deck(deck: DeckCreate):
    return await DeckModel.create(**deck.model_dump())


@router.put("/{deck_id}", response_model=DeckResponse)
@atomic()
async def update_deck(deck_id: int, data: DeckUpdate):
    deck = await DeckModel.get_or_none(id=deck_id)
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deck with ID {deck_id} not found",
        )
    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        return deck
    await deck.update_from_dict(update_data).save()
    return deck

@router.delete("/{deck_id}", status_code=status.HTTP_204_NO_CONTENT)
@atomic()
async def delete_deck(deck_id: int):
    deck = await DeckModel.get_or_none(id=deck_id)
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deck with ID {deck_id} not found",
        )
    await deck.delete()
    return {"detail": "Deck deleted successfully"}

@router.get("/{deck_id}/deck_list", response_model=List[DeckResponseWithCards])
async def get_deck_with_cards(deck_id: int):
    deck = await DeckModel.get_or_none(id=deck_id)
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deck with ID {deck_id} not found",
        )
    deck_cards = await DeckCardModel.filter(deck_id=deck_id).select_related('card')
    # Convert the deck model to the response schema
    deck_list = []
    for dc in deck_cards:
        card = CardInDeckResponse(**dc.card.model_dump(), deck_card_id=dc.id)
        count = 1
        while count <= dc.quantity:
            deck_list.append(card)
            count += 1
    deck_response = deck.model_dump()
    deck_response['cards'] = deck_list
    return DeckResponseWithCards(**deck_response)