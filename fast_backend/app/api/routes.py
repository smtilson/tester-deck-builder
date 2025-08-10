from fastapi import APIRouter
from fast_backend.app.api.endpoints import cards, decks, deck_cards, test

router = APIRouter()

router.include_router(cards.router, prefix="/cards", tags=["cards"])
router.include_router(decks.router, prefix="/decks", tags=["decks"])
router.include_router(deck_cards.router, prefix="/decks", tags=["deck_cards"])
router.include_router(test.router, prefix="/test", tags=["test"])
