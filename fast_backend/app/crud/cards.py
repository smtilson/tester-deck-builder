from typing import Optional
from beanie.odm.fields import PydanticObjectId
from beanie import Link
from datetime import datetime

from fast_backend.app.models import Card as CardModel
from fast_backend.app.schemas import CardCreate, CardUpdate, CardResponse, CardListItem
from fast_backend.app.exceptions import NotFoundException
from fast_backend.app.crud.base_manager import BaseManager
from fast_backend.app.models import Game as GameModel

class CardManager(BaseManager[CardModel, CardCreate, CardUpdate, CardResponse, CardListItem]):
    def __init__(self):
        super().__init__(doc_model=CardModel, response_schema=CardResponse, list_item_schema=CardListItem)

    async def create_from_dict(self, item_data: dict) -> CardModel:
        if "game_id" in item_data:
            game = await GameModel.get(item_data["game_id"])
            if game is None:
                raise NotFoundException(f"No Game with ID {item_data['game_id']} was found.")
            item_data["game"] = game.to_link()
        card_obj = self.doc_model(**item_data)
        await card_obj.insert()
        return card_obj

    
    async def fetch_related(self, item):
        await item.fetch_link(self.doc_model.game)
        
    
