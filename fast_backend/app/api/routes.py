from fastapi import APIRouter
from app.api.endpoints import cards, decks

router = APIRouter()

router.include_router(cards.router, prefix="/cards", tags=["cards"])
router.include_router(decks.router, prefix="/decks", tags=["decks"])
