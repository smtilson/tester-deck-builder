from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class CardBase(BaseModel):
    name: str
    text: Optional[str] = None


class CardCreate(CardBase):
    pass


class CardUpdate(CardBase):
    name: Optional[str] = None
    text: Optional[str] = None
    version: Optional[str] = None


class CardInDB(CardBase):
    id: int
    created_at: datetime
    updated_at: datetime
    version: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CardResponse(CardInDB):
    pass
