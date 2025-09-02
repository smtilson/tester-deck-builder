from typing import Optional
from pydantic import Field
from beanie.odm.fields import PydanticObjectId
from datetime import datetime

from fast_backend.app.schemas import UserResponse
from fast_backend.app.schemas import GameResponse
from .deck_cards import DeckCardListItem
from .users import UserLink
from .games import GameLink
from .base import SettingsSchema

class DeckBase(SettingsSchema):
    name: str
    # maybe this should just be set to 1.0 or something in the create method of the manager.
    # it is already set in the base schema
    #version: str = "1.0.0"

class DeckCreate(DeckBase):
    owner_id: PydanticObjectId
    game_id: PydanticObjectId
    description: Optional[str] = None
    


class DeckUpdate(DeckBase):
    name: Optional[str] = None
    is_public: Optional[bool] = None
    # should the version number be something that is computed?
    version: Optional[str] = None


class DeckResponse(DeckBase):
    id: PydanticObjectId
    owner: UserLink
    game: GameLink
    description: Optional[str] = None
    version: str
    is_public: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

class DeckListItem(DeckBase):
    id: PydanticObjectId
    owner: UserListItem
    game: GameListItem
    is_public: bool

class DeckLink(DeckBase):
    id: PydanticObjectId
    owner: UserLink
    game: GameLink
    is_public: bool

class DeckResponseWithCards(DeckResponse):
    cards: list[DeckCardListItem] = Field(default_factory=list)
