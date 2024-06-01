import sqlite3 as sq


async def create_database():
    global db, cursor
    db = sq.connect('database/database.db')
    cursor = db.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS chat_info(chat_id INT PRIMARY KEY, chat_type TEXT, files_path TEXT)")
    db.commit()


async def create_chat(chat_id: int, chat_type: str, files_path: str):
    chat = cursor.execute(
        f"SELECT 1 FROM chat_info WHERE chat_id == '{chat_id}'").fetchone()
    if not chat:
        cursor.execute(
            f"INSERT INTO chat_info (chat_id, chat_type, files_path) VALUES({chat_id}, '{chat_type}', '{files_path}')")
        db.commit()


async def get_files_path(chat_id: int):
    files_path = cursor.execute(
        f"SELECT files_path FROM chat_info WHERE chat_id == '{chat_id}'").fetchone()
    return files_path


# username
# last_name
# first_name
