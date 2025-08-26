from typing import Optional
from beanie.odm.fields import PydanticObjectId
from beanie import Link
from datetime import datetime

from fast_backend.app.models import Card as CardModel
from fast_backend.app.schemas import CardCreate, CardUpdate, CardResponse, CardListItem
from fast_backend.app.core.exceptions import NotFoundException
from fast_backend.app.crud.base_manager import BaseManager
from fast_backend.app.models import Game as GameModel

class CardManager(BaseManager[CardModel, CardCreate, CardUpdate, CardResponse, CardListItem]):
    def __init__(self):
        super().__init__(doc_model=CardModel, response_schema=CardResponse, list_item_schema=CardListItem)

    async def create(self, item_in: CardCreate) -> Optional[CardResponse]:
        """Create a new card in the database."""
        linked_game : Optional[Link[GameModel]] = None
        card_data = item_in.model_dump(exclude={"game_id"})
        if item_in.game_id:
            game_doc = await GameModel.get(item_in.game_id)
            if not game_doc:
                raise NotFoundException(f"No Game with ID {item_in.game_id} was found.")
            else:
                linked_game = Link(game_doc, document_class=GameModel)
        if linked_game:
            card_data["game"] = linked_game
        card_obj = self.doc_model(**card_data)
        await card_obj.insert()
        if card_obj.id:
            return await self.get(card_obj.id)
        return None

    async def get_model(self, item_id: PydanticObjectId) -> CardModel:
        """Retrieve a card model by its ID."""
        card = await super().get_model(item_id)
        await card.fetch_link(self.doc_model.game)
        return card
    
    async def get_all(self) -> list[CardResponse]:
        cards = await self.doc_model.find_all().to_list()
        for card in cards:
            await card.fetch_link(self.doc_model.game)
        return [self.response_schema.model_validate(card) for card in cards]
    
