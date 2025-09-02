from datetime import datetime
from typing import Optional

from pydantic import Field, BaseModel
from beanie import Document, PydanticObjectId, Link


class BaseDocument(Document):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Settings:
        is_root = False
        use_state_management = True
class MinLink(BaseModel):
    link: Link
    id: PydanticObjectId
    
class BaseLink(MinLink):
    name: str
    version: str

