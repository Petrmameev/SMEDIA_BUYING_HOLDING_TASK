import asyncio
from datetime import datetime, timedelta, timezone

from pyrogram import Client, filters
from pyrogram.errors import BotGroupsBlocked, PeerIdInvalid, UserDeactivated

from config import api_hash, api_id
from db.con_to_db import close_db_connection, create_db_connection
from user import add_user_to_db, fetch_users, update_user_status

CHECK_INTERVAL = 60
STOP_WORDS = ["прекрасно", "ожидать"]

app = Client("SBH20246", api_id=api_id, api_hash=api_hash)

MESSAGES = [
    ("Текст1", timedelta(minutes=6), "msg_1"),
    ("Текст2", timedelta(minutes=39), "msg_2"),
    ("Текст3", timedelta(days=1, hours=2), "msg_3"),
]


async def message_sender():
    conn = await create_db_connection()

    try:
        while True:
            current_time = datetime.now(timezone.utc)
            users = await fetch_users(conn)

            for user in users:
                user_tg_id = user["user_id"]
                user_created_at = user["created_at"]
                user_status = user["status"]
                user_messages = await get_chat_history(app, user_tg_id)

                if user_status not in ["alive", "finished"]:
                    continue

                if any(stop_word in user_messages for stop_word in STOP_WORDS):
                    await update_user_status(conn, user_tg_id, "finished")
                    continue

                try:
                    for message_text, message_delay, msg_id in MESSAGES:
                        if user_status == msg_id or user_status == "alive":
                            sched_time = user_created_at + message_delay
                            if current_time >= sched_time:
                                await app.send_message(user_tg_id, message_text)

                                if message_text == MESSAGES[-1][0]:
                                    await update_user_status(
                                        conn, user_tg_id, "finished"
                                    )
                                else:
                                    await update_user_status(conn, user_tg_id, msg_id)

                except (BotGroupsBlocked, UserDeactivated, PeerIdInvalid) as e:
                    print(f"Cannot send message to {user_tg_id}: {e}")
                    await update_user_status(conn, user_tg_id, "dead")
                except Exception as e:
                    print(f"An unexpected error occurred with {user_tg_id}: {e}")

            await asyncio.sleep(CHECK_INTERVAL)
    finally:
        await close_db_connection(conn)


async def get_chat_history(client, user_id):
    messages = await client.get_history(user_id, limit=100)
    texts = [message.text.lower() for message in messages if message.text]
    return texts


@app.on_message(filters.private & filters.incoming & ~filters.bot)
async def new_user(client, message):
    conn = await create_db_connection()
    try:
        await add_user_to_db(conn, message.from_user.id)
    finally:
        await close_db_connection(conn)


if __name__ == "__main__":
    app.run(message_sender())
