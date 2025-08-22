from datetime import datetime
from typing import Optional

from pydantic import Field
from beanie import Document


class BaseDocument(Document):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Settings:
        is_root = True
