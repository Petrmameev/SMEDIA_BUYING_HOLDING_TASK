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
