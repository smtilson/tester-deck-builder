import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

# Import your models
from fast_backend.app.models import Deck, User, Game, Card

async def main():
    # Connect to MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["test_db"]  # Use your actual test DB name
    await db.decks.drop()
    await db.users.drop()
    await db.games.drop()
    await db.cards.drop()
    # Initialize Beanie (this creates indexes)
    await init_beanie(
        database=db,
        document_models=[Deck, User, Game, Card]  # Add all your models here
    )

    if await Deck.find().count() == 0:
    
        user = User(username="dummy", email="dummy@example.com", hashed_password="dnkjsfhlnqknlfqwf")
        await user.insert()
        game = Game(name="dummy_game")
        await game.insert()
        deck = Deck(name="dummy_deck", owner=user, game=game, version="1.0.0")
        await deck.insert()
    
    # Inspect indexes for Deck collection
    indexes = await db.decks.index_information()
    print("Deck indexes:")
    for name, info in indexes.items():
        print(f"{name}: {info}")

    # You can inspect other collections similarly:
    # indexes = await db.users.index_information()
    # print("User indexes:", indexes)

if __name__ == "__main__":
    asyncio.run(main())