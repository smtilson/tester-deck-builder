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
        
    async def create(self, item_in: DeckCreate) -> DeckResponse:
        deck_data = item_in.model_dump(exclude={"owner_id","game_id"})
        owner = await User.get(item_in.owner_id)
        game = await Game.get(item_in.game_id)
        del deck_data["version"]
        deck_obj = await self.doc_model.create(**deck_data)
        deck_obj.owner = cast(Link[User], owner)
        deck_obj.game = cast(Link[Game],game)
        await deck_obj.insert()
        if deck_obj.id:
            return await self.get(deck_obj.id)
        raise Exception(f"There was an error creating a deck based on {item_in}.")
