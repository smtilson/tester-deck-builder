import pytest
from fast_backend.app.models.cards import Card

@pytest.mark.skip("basic")
@pytest.mark.asyncio
async def test_insert_card(db_client):
    test_card = Card(name="Sanity Check", text="...")
    await test_card.insert()

    found = await Card.find_one(Card.name == "Sanity Check")
    assert found is not None
    assert found.name == "Sanity Check"