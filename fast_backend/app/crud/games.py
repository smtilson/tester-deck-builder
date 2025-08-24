from typing import Optional
from beanie.odm.fields import PydanticObjectId
from datetime import datetime
from beanie import Link

from fast_backend.app.models.games import Game as GameModel
from fast_backend.app.schemas.games import GameCreate, GameUpdate, GameResponse, GameListItem
from fast_backend.app.models.users import User
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
        linked_designers : Optional[list[Link[User]]] = None
        linked_developers : Optional[list[Link[User]]] = None
        game_data = item_in.model_dump(exclude={"designer_ids", "developer_ids"})
        if item_in.designer_ids:
            designers = await User.find(User.id.in_(item_in.designer_ids)).to_list()
            linked_designers = [Link(designer, document_class=User) for designer in designers]
        if item_in.developer_ids:
            developers = await User.find(User.id.in_(item_in.developer_ids)).to_list()
            linked_developers = [Link(developer, document_class=User) for developer in developers]
        game_obj = self.doc_model(**game_data)
        game_obj.designers = linked_designers if linked_designers else list()
        game_obj.developers = linked_developers if linked_developers else list()
        await game_obj.insert()
        if game_obj.id:
            return await self.get(game_obj.id)
        return None


game_manager = GameManager()