from typing import Optional, cast
from beanie.odm.fields import PydanticObjectId
from beanie import Link

from fast_backend.app.models import Deck as DeckModel
from fast_backend.app.models import User
from fast_backend.app.models import Game
from fast_backend.app.schemas import (
    DeckCreate,
    DeckUpdate,
    DeckResponse,
    DeckListItem
)

from fast_backend.app.crud.base_manager import BaseManager

class DeckManager(BaseManager[DeckModel, DeckCreate, DeckUpdate, DeckResponse, DeckListItem]):
    def __init__(self):
        super().__init__(doc_model=DeckModel, response_schema=DeckResponse, list_item_schema=DeckListItem)

    async def fetch_related(self, item: DeckModel):
        await item.fetch_link(self.doc_model.owner)
        await item.fetch_link(self.doc_model.game)

    async def create_from_dict(self, item_data: dict) -> DeckModel:
        owner = await User.get(item_data["owner_id"])
        game = await Game.get(item_data["game_id"])
        owner = cast(Link[User], owner)
        game = cast(Link[Game], game)
        item_data["owner"] = owner
        item_data["game"] = game
        del item_data["owner_id"]
        del item_data["game_id"]
        deck_obj = self.doc_model(**item_data)
        await deck_obj.insert()
        return deck_obj
