from typing import Optional
from pydantic import Field
from beanie.odm.fields import PydanticObjectId
from datetime import datetime

from fast_backend.app.schemas.users import UserResponse
from .deck_cards import DeckCardListItem
from .users import UserListItem
from .games import GameListItem
from .base import BaseSchema

class DeckBase(BaseSchema):
    name: str
    version: str = "0.0.0"

class DeckCreate(DeckBase):
    owner_id: PydanticObjectId
    game_id: PydanticObjectId
    description: Optional[str] = None
    is_public: bool = Field(default=False)
    


class DeckUpdate(DeckBase):
    name: Optional[str] = None
    is_public: Optional[bool] = None
    version: Optional[str] = None


class DeckResponse(DeckBase):
    id: PydanticObjectId
    owner: UserListItem
    game: GameListItem
    description: Optional[str] = None
    is_public: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class DeckResponseWithCards(DeckResponse):
    cards: list[DeckCardListItem] = Field(default_factory=list)
