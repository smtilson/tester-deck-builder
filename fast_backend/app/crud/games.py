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

    async def get_model(self, item_id: PydanticObjectId) -> GameModel:
        game = await super().get_model(item_id)
        await game.fetch_link(self.doc_model.designers)
        await game.fetch_link(self.doc_model.developers)
        return game

    async def create(self, item_in: GameCreate) -> Optional[GameResponse]:
        game_data = item_in.model_dump(exclude={"designer_ids", "developer_ids"})
        designer_id_set = set(item_in.designer_ids or [])
        developer_id_set = set(item_in.developer_ids or [])
        all_ids = list(designer_id_set | developer_id_set)
        designers = []
        developers = []
        if all_ids:
            users = await User.find({"_id": {"$in": all_ids}}).to_list()
            designers = [u for u in users if u.id in designer_id_set]
            developers = [u for u in users if u.id in developer_id_set]
        game_obj = self.doc_model(**game_data)
        game_obj.designers = cast(Sequence[Link[User]], designers)
        game_obj.developers = cast(Sequence[Link[User]], developers)
        await game_obj.insert()
        
        if game_obj.id:
            return await self.get(game_obj.id)
        return None