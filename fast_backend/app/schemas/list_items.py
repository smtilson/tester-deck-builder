from beanie.odm.fields import PydanticObjectId
from typing import Optional

from fastapi_users.schemas import CreateUpdateDictModel as CUDM
from .base import SettingsSchema



class ListItem(SettingsSchema):
    id: PydanticObjectId

class UserListItem(ListItem, CUDM):
    username: str


class GameListItem(ListItem):    
    name: str
    version: str = "0.0.0"

class CardListItem(ListItem):
    name: str
    version: str = "0.0.0"
    game: Optional[GameListItem] = None


class DeckListItem(ListItem):
    name: str
    owner: UserListItem
    game: GameListItem
    is_public: bool