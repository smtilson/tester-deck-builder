from typing import Optional
from beanie import PydanticObjectId
from pydantic import Field, BaseModel
from datetime import datetime

from .games import Game
from .cards import Card


class DeckCard(BaseModel):
    original_card_id: PydanticObjectId
    game_id: PydanticObjectId
    quantity: int = Field(default=1)
    name: str
    text: Optional[str] = None
    # card_type: str = Field(default="")
    # traits: list[str] = Field(default_factory=list)
    # image_url: Optional[str] = Field(default="")
    # should this be a computed field
    # in_sync: bool = Field(default=True)
    # necessary because it doesn't inherit from BaseDocument
    version: str = "0.0.0"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
