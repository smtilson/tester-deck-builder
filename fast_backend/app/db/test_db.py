import asyncio
from tortoise import Tortoise


async def test_connection():
    # Replace with your actual URI
    db_url = "postgres://s_user:yadda@localhost:5432/tester_deck_builder"

    try:
        await Tortoise.init(db_url=db_url, modules={"models": []})
        conn = Tortoise.get_connection("default")
        await conn.execute_query("SELECT 1")
        print("Database connection successful!")
    except Exception as e:
        print(f"Error connecting to database: {e}")
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(test_connection())
