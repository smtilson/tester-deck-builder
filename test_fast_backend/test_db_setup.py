import pytest
from fast_backend.app.models.cards import Card
from fast_backend.app.crud.cards import CardRepo
from fast_backend.app.schemas.cards import CardCreate


async def test_db_is_configured_correctly(init_db):
    """
    Verifies that the database and Tortoise ORM are correctly configured
    by creating a single user and checking if it exists.
    """
    # Ensure the 'db' fixture is requested as a parameter.
    # This will trigger the entire setup chain from your conftest.py.

    # Define a user using your Pydantic schema
    card_data = CardCreate(**{"name": "Test Card", "description": "A card for testing"})

    # Use your UserRepo to create the user, which requires the DB connection
    created_card = await CardRepo.create_card(card_data)

    # Assert the user object was created and has a valid ID
    assert created_card is not None
    assert created_card.id is not None
    assert created_card.name == "Test Card"

    # Directly query the database to verify the card exists
    db_card = await Card.get_or_none(id=created_card.id)
    assert db_card is not None
    assert db_card.id == created_card.id
