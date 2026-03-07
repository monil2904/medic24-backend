import asyncpg
from app.config import settings

pool = None

async def init_db_pool():
    global pool
    pool = await asyncpg.create_pool(settings.DATABASE_URL)

async def close_db_pool():
    global pool
    if pool is not None:
        await pool.close()

def get_pool():
    return pool

async def execute(query: str, *args):
    async with pool.acquire() as connection:
        return await connection.execute(query, *args)

async def fetch_one(query: str, *args):
    async with pool.acquire() as connection:
        return await connection.fetchrow(query, *args)

async def fetch_all(query: str, *args):
    async with pool.acquire() as connection:
        return await connection.fetch(query, *args)
