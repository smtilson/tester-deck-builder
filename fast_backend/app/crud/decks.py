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
from fast_backend.app.exceptions import NotFoundException, UserNotExists

class DeckManager(BaseManager[DeckModel, DeckCreate, DeckUpdate, DeckResponse, DeckListItem]):
    def __init__(self):
        super().__init__(doc_model=DeckModel, response_schema=DeckResponse, list_item_schema=DeckListItem)

    async def fetch_related(self, item: DeckModel):
        await item.fetch_link(self.doc_model.owner)
        await item.fetch_link(self.doc_model.game)

    async def create_from_dict(self, item_data: dict) -> DeckModel:
        owner = await User.get(item_data["owner_id"])
        if owner is None:
            raise UserNotExists(f"User with id {item_data['owner_id']} does not exist")
        game = await Game.get(item_data["game_id"])
        if game is None:
            raise NotFoundException(f"Game with id {item_data['game_id']} does not exist")
        item_data["owner"] = owner.to_link() if owner else None
        item_data["game"] = game.to_link() if game else None
        del item_data["owner_id"]
        del item_data["game_id"]
        deck_obj = self.doc_model(**item_data)
        await deck_obj.insert()
        return deck_obj
