from datetime import datetime
from typing import Optional

from pydantic import Field
from beanie import Document, Indexed
from .base import BasicModel

class Card(BasicModel):
    """
    Represents a Magic: The Gathering card.
    """
    name: Indexed(str, unique=True)
    game: str
    card_type: str = Field(default="")
    traits: list[str] = Field(default_factory=list)
    text: Optional[str] = None
    collector_number: Optional[str] = None
    image_url: Optional[str] = None
    version: str
    
    class Settings:
        name = "cards"
        use_state_management = True  # Enable state management for this model
