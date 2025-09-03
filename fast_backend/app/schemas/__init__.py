"""
Pydantic schemas for request/response models.
"""

from .users import UserResponse, UserCreate, UserUpdatePermissions, UserLogin, UserUpdate
from .cards import CardCreate, CardUpdate, CardResponse
from .decks import DeckCreate, DeckUpdate, DeckResponse, DeckResponseWithCards 
from .deck_cards import DeckCardCreate, DeckCardUpdate, DeckCardResponse, DeckCardListItem
from .games import GameCreate, GameUpdate, GameResponse
from .list_items import UserListItem, GameListItem, CardListItem, DeckListItem


# --- Model rebuilds for forward references ---
UserResponse.model_rebuild()
UserListItem.model_rebuild()
UserUpdatePermissions.model_rebuild()
CardResponse.model_rebuild()
CardListItem.model_rebuild()
DeckResponse.model_rebuild()
DeckResponseWithCards.model_rebuild()
DeckListItem.model_rebuild()
DeckCardResponse.model_rebuild()
DeckCardListItem.model_rebuild()
GameResponse.model_rebuild()
GameListItem.model_rebuild()


__all__ = [
    "UserResponse",
    "UserCreate",
    "UserUpdate",
    "UserUpdatePermissions",
    "UserListItem",
    "UserLogin",
    "CardCreate",
    "CardUpdate",
    "CardResponse",
    "CardListItem",
    "DeckCreate",
    "DeckUpdate",
    "DeckResponse",
    "DeckResponseWithCards",
    "DeckListItem",
    "DeckCardCreate",
    "DeckCardUpdate",
    "DeckCardResponse",
    "DeckCardListItem",
    "GameCreate",
    "GameUpdate",
    "GameResponse",
    "GameListItem",
]
