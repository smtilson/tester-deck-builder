from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
import uuid
from datetime import datetime
from .deck_cards import CardInDeckResponse
from fast_backend.app.schemas.users import UserResponse


class DeckBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_valid: bool = False


class DeckCreate(DeckBase):
    owner: UserResponse


class DeckUpdate(DeckBase):
    name: Optional[str] = None
    description: Optional[str] = None
    is_valid: Optional[bool] = None
    owner: Optional[UserResponse] = None


class DeckInDB(DeckBase):
    id: int
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class DeckResponse(DeckInDB):
    pass


class DeckResponseWithCards(DeckResponse):
    cards: list[CardInDeckResponse] = Field(default_factory=list)
