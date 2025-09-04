from beanie import Link, PydanticObjectId
from pydantic import BaseModel
from typing import ClassVar, Type

#from .users import User
#from .games import Game
#from .decks import Deck
#from .cards import Card

from fast_backend.app.schemas import UserListItem, GameListItem, DeckListItem, CardListItem


class MinLink(BaseModel):
    link: Link
    id: PydanticObjectId
    list_item_class: ClassVar[Type] = None

    # how will type hints for this work.
    def to_list_item(self):
        if self.list_item_class is None:
            raise NotImplementedError(
                "to_list_item method must be implemented in subclasses"
            )
        data = self.model_dump(exclude={"link"})
        return self.list_item_class(**data)


class BaseLink(MinLink):
    name: str
    version: str

class GameLink(BaseLink):
    link: Link["Game"]

    list_item_class = GameListItem
    
    @classmethod
    def from_instance(cls, instance):
        return cls(
            link=Link[type(instance)](instance.id, type(instance)),
            id=instance.id,
            name=instance.name,
            version=instance.version,
        )


class UserLink(MinLink):
    link: Link["User"]
    username: str
    
    list_item_class = UserListItem
    
    @classmethod
    def from_instance(cls, instance):
        return cls(
            link=Link[type(instance)](instance.id, type(instance)),
            id=instance.id,
            username=instance.username,
        )
    
class DeckLink(BaseLink):
    link: Link["Deck"]
    owner: UserLink
    game: GameLink
    is_public: bool
    
    list_item_class = DeckListItem
    
    @classmethod
    def from_instance(cls, instance):
        owner_link = UserLink.from_instance(instance.owner)
        game_link = GameLink.from_instance(instance.game)
        return cls(
            link=Link[type(instance)](instance.id, type(instance)),
            id=instance.id,
            name=instance.name,
            version=instance.version,
            owner=owner_link,
            game=game_link,
            is_public=instance.is_public
        )

    def to_list_item(self):
        if self.list_item_class is None:
            raise NotImplementedError("to_list_item method must be implemented in subclasses")
        data = self.model_dump(exclude={"link", "version"})
        data["game"] = self.game.to_list_item()
        data["owner"] = self.owner.to_list_item()
        # Convert nested game link to GameListItem if present
        return self.list_item_class(**data)

class CardLink(BaseLink):
    link: Link["Card"]
    game: GameLink
    
    list_item_class = CardListItem
    
    @classmethod
    def from_instance(cls, instance):
        game_link = GameLink.from_instance(instance.game)
        return cls(
            link=Link[type(instance)](instance.id, type(instance)),
            id=instance.id,
            name=instance.name,
            version=instance.version,
            game=game_link
        )

    def to_list_item(self):
        if self.list_item_class is None:
            raise NotImplementedError("to_list_item method must be implemented in subclasses")
        data = self.model_dump(exclude={"link"})
        if self.game is not None:
            data["game"] = self.game.to_list_item()
        # Convert nested game link to GameListItem if present
        return self.list_item_class(**data)
