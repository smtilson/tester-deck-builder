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

    async def get_model(self, deck_id: PydanticObjectId) -> DeckModel:
        deck = await super().get_model(deck_id)
        await deck.fetch_link(self.doc_model.owner)
        await deck.fetch_link(self.doc_model.game)
        return deck
    async def create_from_dict(self, item_data: dict) -> DeckModel:
        owner = await User.get(item_data["owner_id"])
        game = await Game.get(item_data["game_id"])
        del item_data["owner_id"]
        del item_data["game_id"]
        deck_obj = self.doc_model(**item_data)
        deck_obj.owner = cast(Link[User], owner)
        deck_obj.game = cast(Link[Game],game)
        await deck_obj.insert()
        return deck_obj
    #refactor this to use create_from_dict   
