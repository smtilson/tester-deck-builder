import asyncio



async def sample_connection():
    # Replace with your actual URI
    db_url = ""

    try:
        #await Tortoise.init(db_url=db_url, modules={"models": []})
        #conn = Tortoise.get_connection("default")
        #await conn.execute_query("SELECT 1")
        print("Database connection successful!")
    except Exception as e:
        print(f"Error connecting to database: {e}")
    finally:
        #await Tortoise.close_connections()
        return

if __name__ == "__main__":
    asyncio.run(sample_connection())
