from fast_backend.app.schemas.decks import DeckCreate
from fast_backend.app.models.decks import (
    Deck as DeckModel,
    DeckCard as DeckCardModel,
)
from fast_backend.app.crud.decks import DeckCrud


async def create_deck(deck_data: DeckCreate, owner_id: int = 1):
    """
    Create a deck with its cards.

    Args:
        deck_data: The deck data from the request
        owner_id: The ID of the deck owner (default: 1 for testing)

    Returns:
        The created deck as a Pydantic model
    """
    cards_data = deck_data.cards
    deck_dict = deck_data.dict(exclude={"cards"})

    # Set the owner ID
    deck_dict["owner_id"] = owner_id

    # Create deck
    deck_obj = await DeckModel.create(**deck_dict)

    # Add cards to deck
    for card_data in cards_data:
        await DeckCardModel.create(
            deck_id=deck_obj.id, card_id=card_data.card_id, quantity=card_data.quantity
        )

    # Refresh deck with related cards
    await deck_obj.fetch_related("deck_cards__card")
    return #await Deck.from_tortoise_orm(deck_obj)


async def add_card_to_deck(deck_id: int, card_id: int, quantity: int = 1):
    """
    Add a card to a deck or increase its quantity if it already exists.

    Args:
        deck_id: The ID of the deck
        card_id: The ID of the card to add
        quantity: The quantity to add (default: 1)

    Returns:
        True if successful, False if the deck doesn't exist
    """
    # Check if deck exists
    deck_exists = await DeckModel.filter(id=deck_id).exists()
    if not deck_exists:
        return False

    # Check if card is already in deck
    deck_card = await DeckCardModel.filter(deck_id=deck_id, card_id=card_id).first()

    if deck_card:
        # Increase quantity
        deck_card.quantity += quantity
        await deck_card.save()
    else:
        # Add new card
        await DeckCardModel.create(deck_id=deck_id, card_id=card_id, quantity=quantity)

    return True
