from pyrogram import Client, filters

from db.con_to_db import close_db_connection, create_db_connection
from logic import app


@app.on_message(filters.private & filters.incoming & ~filters.bot)
async def new_user(client, message):
    conn = await create_db_connection()
    try:
        await add_user_to_db(conn, message.from_user.id)
    finally:
        await close_db_connection(conn)


async def add_user_to_db(conn, user_tg_id):
    await conn.execute(
        """
        INSERT INTO users (user_id, status) VALUES ($1, 'alive')
        ON CONFLICT (user_id) DO NOTHING
    """,
        user_tg_id,
    )


async def update_user_status(conn, user_tg_id, new_status):
    await conn.execute(
        """
            UPDATE users
            SET status = $1, status_updated_at = NOW()
            WHERE user_id = $2
        """,
        new_status,
        user_tg_id,
    )


async def fetch_users(conn):
    return await conn.fetch(
        """
        SELECT * FROM users
        WHERE status = 'alive' OR status = 'msg_1' OR status = 'msg_2'
    """
    )
