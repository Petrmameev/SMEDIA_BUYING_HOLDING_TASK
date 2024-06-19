import asyncio

import asyncpg

from config import database, host, password, user


async def create_db():
    conn = await asyncpg.connect(
        user=user, password=password, database=database, host=host
    )
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            status TEXT NOT NULL,
            status_updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    await conn.close()


loop = asyncio.get_event_loop()
loop.run_until_complete(create_db())

if __name__ == "__main__":
    create_db()
