from typing import Optional
from datetime import datetime

from beanie.odm.fields import PydanticObjectId

from .base import SettingsSchema
from .list_items import UserListItem, GameListItem

class GameBase(SettingsSchema):
    name: str
    version: str = "0.0.0"


class GameCreate(GameBase):
    description: Optional[str] = None
    designer_ids: Optional[list[PydanticObjectId]] = None
    developer_ids: Optional[list[PydanticObjectId]] = None
    publisher: Optional[str] = None
    release_date: Optional[datetime] = None
    

class GameUpdate(GameCreate):
    name: Optional[str] = None
    version: Optional[str] = None
    

class GameResponse(GameListItem):
    description: Optional[str] = None
    designers: Optional[list[UserListItem]] = None
    developers: Optional[list[UserListItem]] = None
    publisher: Optional[str] = None
    release_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

