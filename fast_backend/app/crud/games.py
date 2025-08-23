from typing import Optional
from beanie.odm.fields import PydanticObjectId
from datetime import datetime

from fast_backend.app.models.games import Game as GameModel
from fast_backend.app.schemas.games import GameCreate, GameUpdate, GameResponse
from fast_backend.app.core.exceptions import NotFoundException
from fast_backend.app.crud.base_manager import BaseManager

class GameManager(BaseManager[GameModel, GameCreate, GameUpdate, GameResponse]):
    pass

game_manager = GameManager(doc_model=GameModel, response_schema=GameResponse)

class OldGameManager:

    @staticmethod
    async def create(game_in: GameCreate) -> GameResponse:
        """
            Create a game.

        Args:
            game_data: The game data from the request

        Returns:
            The created game as a Pydantic schema instance.
        """
        game_obj = GameModel(**game_in.model_dump())
        await game_obj.insert()
        return GameResponse.model_validate(game_obj)

    @staticmethod
    async def get_model(game_id: PydanticObjectId) -> GameModel:
        """
        Get a game by its ID.

        Args:
            game_id: The ID of the game to retrieve

        Returns:
            The game as a Pydantic schema, or None if it doesn't exist.
        """
        print("get_model called")
        game_model = await GameModel.get(game_id)
        if not game_model:
            print("record not found")
            raise NotFoundException(f"No Game with ID {game_id} was found.")
        print("record found")
        print("exiting get_model")
        return game_model

    @staticmethod
    async def get(game_id: PydanticObjectId) -> Optional[GameResponse]:
        """
        Get a game by its ID.

        Args:
            game_id: The ID of the game to retrieve

        Returns:
            The game as a Pydantic schema, or None if it doesn't exist.
        """
        print("get called")
        game_obj = await GameManager.get_model(game_id)
        print("game model found.")
        print("converting to GameResponse and exiting get game")
        return GameResponse.model_validate(game_obj)

    @staticmethod
    async def get_alls() -> list[GameResponse]:
        """
        Get all games.

        Returns:
            A list of all games as Pydantic schema instances.
        """
        game_objs = await GameModel.find_all().to_list()
        return [GameResponse.model_validate(game) for game in game_objs]

    @staticmethod
    async def update(
        game_id: PydanticObjectId, game_data: GameUpdate
    ) -> Optional[GameResponse]:
        """
        Update a game.

        Args:
            game_id: The ID of the game to update
            game_data: The updated game data from the request

        Returns:
            The updated game as a Pydantic schema, or None if the game doesn't exist.
        """
        game_obj = await GameManager.get_model(game_id)
        update_data = game_data.model_dump(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.now()
            await game_obj.set(update_data)
            await game_obj.save()
        return GameResponse.model_validate(game_obj)

    @staticmethod
    async def delete(game_id: PydanticObjectId) -> bool:
        """
        Delete a game.

        Args:
            game_id: The ID of the game to delete

        Returns:
            True if the game was deleted, False if it doesn't exist
        """
        print("delete game called")
        game_obj = await GameManager.get_model(game_id)
        print("game found for deletion")
        await game_obj.delete()
        print("game deleted")
        return True
