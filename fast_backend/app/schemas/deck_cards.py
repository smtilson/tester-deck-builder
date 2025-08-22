from pydantic import BaseModel
from beanie.odm.fields import PydanticObjectId
from datetime import datetime
from typing import Optional

from .cards import CardListItem


class DeckCardBase(BaseModel):
    quantity: int = 1


class DeckCardCreate(DeckCardBase):
    original_card_id: PydanticObjectId
    # I guess that all I want to submit here is the original card id, the rest is gotten by the process
    # and added ebhind the scenes
    # deck_id is not included as it will be provided by the url


class DeckCardUpdate(DeckCardCreate):
    pass

class AddDeckCards(BaseModel):
    cards: list[DeckCardCreate]

class DeckCardListItem(DeckCardBase):
    original_card: CardListItem
    # no deck id because this is contained in the deck
    #deck_id: PydanticObjectId
    #created_at: datetime
    #updated_at: datetime

class DeckCardResponse(DeckCardListItem):
    created_at: datetime 
    updated_at: Optional[datetime] = None
    