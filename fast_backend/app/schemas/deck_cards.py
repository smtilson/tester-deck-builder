from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from .cards import CardResponse


class DeckCardBase(BaseModel):
    # card_id and deck_id are not included in the base schema
    # because they aren't properties of the relation, they will
    # be included when we create the relationship.
    quantity: int = 1
    

class DeckCardCreate(BaseModel):
    card_id: int
    # deck_id is not included as it will be provided by the url        

class DeckCardUpdate(DeckCardBase):
    quantity: Optional[int] = None


class DeckCardInDB(DeckCardBase):
    id: int
    card_id: int
    deck_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Schema for the response when showing cards within a deck
class DeckCardResponse(DeckCardInDB):
    pass

class DeckCardResponseWithCard(DeckCardResponse):
    card: CardResponse
    
class CardInDeckResponse(CardResponse):
    deck_card_id: int
    model_config = ConfigDict(from_attributes=True)





