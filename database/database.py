import sqlite3 as sq

from database.errors import DBCreationError, ChatCreationError, ChatPathError

async def create_database():
    global db, cursor
    try:
        db = sq.connect('database/database.db')
        cursor = db.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS chat_info(chat_id INT PRIMARY KEY, chat_type TEXT, files_path TEXT)")
        db.commit()
    except Exception as e:
        raise DBCreationError() from e


async def create_chat(chat_id: int, chat_type: str, files_path: str):
    try:
        chat = cursor.execute(
            f"SELECT 1 FROM chat_info WHERE chat_id == '{chat_id}'").fetchone()
        if not chat:
            cursor.execute(
                f"INSERT INTO chat_info (chat_id, chat_type, files_path) VALUES({chat_id}, '{chat_type}', '{files_path}')")
            db.commit()
    except Exception as e:
        raise ChatCreationError(chat_id) from e


async def get_files_path(chat_id: int):
    files_path = ""
    try:
        files_path = cursor.execute(
            f"SELECT files_path FROM chat_info WHERE chat_id == '{chat_id}'").fetchone()
    except Exception as e:
        raise ChatPathError(chat_id) from e
    return files_path


# username
# last_name
# first_name
