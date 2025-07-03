from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from .cards import Card


class DeckCardBase(BaseModel):
    card_id: int
    quantity: int = 1


class DeckCardCreate(DeckCardBase):
    pass


class DeckCardUpdate(DeckCardBase):
    quantity: Optional[int] = None


class DeckCardInDB(DeckCardBase):
    id: int
    deck_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class DeckBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_valid: bool = False


class DeckCreate(DeckBase):
    cards: List[DeckCardCreate]


class DeckUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_valid: Optional[bool] = None
    cards: Optional[List[DeckCardCreate]] = None


class DeckInDB(DeckBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Deck(DeckInDB):
    cards: List[Card] = []
