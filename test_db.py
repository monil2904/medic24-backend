import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")

async def test_db():
    print(f"Connecting to: {db_url}")
    try:
        conn = await asyncpg.connect(db_url)
        print("Success!")
        await conn.close()
    except Exception as e:
        import traceback
        traceback.print_exc()

asyncio.run(test_db())
