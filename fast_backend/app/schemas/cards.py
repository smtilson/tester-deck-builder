from typing import Optional
from beanie.odm.fields import PydanticObjectId
from datetime import datetime

from .base import SettingsSchema
from .games import GameLink


class CardBase(SettingsSchema):
    name: str
    version: str = "0.0.0"
    


class CardCreate(CardBase):
    game_id: Optional[PydanticObjectId] = None
    text: Optional[str] = None

class CardUpdate(CardBase):
    name: Optional[str] = None
    text: Optional[str] = None
    version: Optional[str] = None

class CardLink(CardBase):
    id: PydanticObjectId
    game: Optional[GameLink] = None

class CardResponse(CardListItem):
    text: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None