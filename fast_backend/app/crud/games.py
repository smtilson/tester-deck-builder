from typing import Optional, cast, Sequence
from beanie.odm.fields import PydanticObjectId
from datetime import datetime
from beanie import Link

from fast_backend.app.models import Game as GameModel
from fast_backend.app.schemas import GameCreate, GameUpdate, GameResponse, GameListItem
from fast_backend.app.models import User
from fast_backend.app.core.exceptions import NotFoundException
from fast_backend.app.crud.base_manager import BaseManager

class GameManager(BaseManager[GameModel, GameCreate, GameUpdate, GameResponse, GameListItem]):
    def __init__(self):
        super().__init__(doc_model=GameModel, response_schema=GameResponse, list_item_schema=GameListItem)

    async def fetch_related(self, item: GameModel):
        await item.fetch_link(self.doc_model.designers)
        await item.fetch_link(self.doc_model.developers)

    async def create_from_dict(self, item_data: dict) -> GameModel:
        designer_id_set = set(item_data["designer_ids"] or [])
        developer_id_set = set(item_data["developer_ids"] or [])
        del item_data["designer_ids"]
        del item_data["developer_ids"]
        game_obj = self.doc_model(**item_data)
        if designer_id_set:
            designers = await User.find({"_id":
                {"$in": list(designer_id_set)}}).to_list()
            if designers:
                game_obj.designers = cast(Sequence[Link[User]], designers)
        if developer_id_set:
            developers = await User.find({"_id": 
                {"$in": list(developer_id_set)}}).to_list()
            if developers:
                game_obj.developers = cast(Sequence[Link[User]], developers)
        await game_obj.insert()
        return game_obj

    async def get_by_name(self, name: str) -> GameResponse:
        return await self._get_by_key("name", name)
