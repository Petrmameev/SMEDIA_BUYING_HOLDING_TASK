import asyncpg

from config import database, host, password, user


async def create_db_connection():
    conn = await asyncpg.connect(
        user=user, password=password, database=database, host=host
    )
    return conn


async def close_db_connection(conn):
    await conn.close()


async def fetch_users(conn):
    return await conn.fetch("SELECT * FROM users WHERE status = 'alive'")
