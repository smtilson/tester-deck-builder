from typing import Optional
from beanie.odm.fields import PydanticObjectId
from datetime import datetime

from .base import BaseSchema
from .games import GameListItem


class CardBase(BaseSchema):
    name: str
    version: str = "0.0.0"
    


class CardCreate(CardBase):
    game: Optional[GameListItem] = None
    text: Optional[str] = None

class CardUpdate(CardCreate):
    name: Optional[str] = None
    version: Optional[str] = None

class CardListItem(CardBase):
    id: PydanticObjectId
    game: Optional[GameListItem] = None

class CardResponse(CardListItem):
    text: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None