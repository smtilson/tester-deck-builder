from typing import Optional
from beanie import Link, PydanticObjectId
from pydantic import Field, BaseModel
from datetime import datetime

from .games import Game
from .cards import Card

class DeckCard(BaseModel):
    original_card: Link[Card]
    in_sync: bool = Field(default=True)
    game: Link[Game]
    quantity: int = Field(default=1)
    name: str
    card_type: str = Field(default="")
    traits: list[str] = Field(default_factory=list)
    text: Optional[str] = None
    collector_number: Optional[str] = None
    image_url: Optional[str] = None
    version: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)