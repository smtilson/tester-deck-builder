from typing import List
from fastapi import APIRouter, HTTPException, status
from tortoise.exceptions import DoesNotExist
from tortoise.transactions import atomic

from app.api.models.decks import Deck as DeckModel, DeckCard as DeckCardModel
from app.api.schemas.decks import Deck, DeckCreate, DeckUpdate, DeckCardCreate

router = APIRouter()


@router.get("/", response_model=List[Deck])
async def get_decks():
    return await Deck.from_queryset(
        DeckModel.all().prefetch_related("deck_cards__card")
    )


@router.get("/{deck_id}", response_model=Deck)
async def get_deck(deck_id: int):
    try:
        return await Deck.from_queryset_single(
            DeckModel.get(id=deck_id).prefetch_related("deck_cards__card")
        )
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deck with ID {deck_id} not found",
        )


@router.post("/", response_model=Deck, status_code=status.HTTP_201_CREATED)
@atomic()
async def create_deck(deck: DeckCreate):
    return await Deck.create(deck)


@router.put("/{deck_id}", response_model=Deck)
@atomic()
async def update_deck(deck_id: int, deck: DeckUpdate):
    try:
        # Check if deck exists
        await DeckModel.get(id=deck_id)

        # Update deck attributes
        if any(
            key in deck.dict(exclude_unset=True)
            for key in ["name", "description", "is_valid"]
        ):
            await DeckModel.filter(id=deck_id).update(
                **{
                    k: v
                    for k, v in deck.dict(exclude_unset=True).items()
                    if k != "cards"
                }
            )

        # Update cards if provided
        if deck.cards is not None:
            # Remove existing cards
            await DeckCardModel.filter(deck_id=deck_id).delete()

            # Add updated cards
            for card_data in deck.cards:
                await DeckCardModel.create(
                    deck_id=deck_id,
                    card_id=card_data.card_id,
                    quantity=card_data.quantity,
                )

        # Return updated deck
        return await Deck.from_queryset_single(
            DeckModel.get(id=deck_id).prefetch_related("deck_cards__card")
        )
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deck with ID {deck_id} not found",
        )


@router.delete("/{deck_id}", status_code=status.HTTP_204_NO_CONTENT)
@atomic()
async def delete_deck(deck_id: int):
    try:
        # Check if deck exists
        await DeckModel.get(id=deck_id)

        # Delete associated deck cards first
        await DeckCardModel.filter(deck_id=deck_id).delete()

        # Delete the deck
        await DeckModel.filter(id=deck_id).delete()
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deck with ID {deck_id} not found",
        )
