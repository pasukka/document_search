import sqlite3 as sq

from database.errors import DBCreationError, ChatCreationError, ChatPathError, ChatDeletionError, DBClosingError
from loggers.loggers import DBLogger

db_logger = DBLogger()

async def create_database():
    global db, cursor
    try:
        db = sq.connect('database/database.db', timeout=10)
        cursor = db.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS chat_info(chat_id INT PRIMARY KEY, chat_type TEXT, files_path TEXT)")
        db.commit()
        db_logger.logger.info("Created db")
    except Exception as e:
        db_logger.logger.error("Error while creating db")
        db_logger.logger.exception(e)
        raise DBCreationError() from e


async def create_chat(chat_id: int, chat_type: str, files_path: str):
    try:
        chat = cursor.execute(
            f"SELECT 1 FROM chat_info WHERE chat_id == '{chat_id}'").fetchone()
        if not chat:
            cursor.execute(
                f"INSERT INTO chat_info (chat_id, chat_type, files_path) VALUES({chat_id}, '{chat_type}', '{files_path}')")
            db.commit()
        db_logger.logger.info(f"Created chat {chat_id}")
    except Exception as e:
        db_logger.logger.error(f"Error while creating chat {chat_id}")
        db_logger.logger.exception(e)
        raise ChatCreationError(chat_id) from e


async def delete_chat(chat_id: int):
    try:
        cursor.execute(
            f"DELETE FROM chat_info WHERE chat_id == '{chat_id}'").fetchone()
        db.commit()
        db_logger.logger.info(f"Deleted chat {chat_id}")
    except Exception as e:
        db_logger.logger.error(f"Error while deleting chat {chat_id}")
        db_logger.logger.exception(e)
        raise ChatDeletionError(chat_id) from e


async def get_files_path(chat_id: int):
    files_path = ""
    try:
        files_path = cursor.execute(
            f"SELECT files_path FROM chat_info WHERE chat_id == '{chat_id}'").fetchone()
        db_logger.logger.info(f"Get files path for chat {chat_id}")
    except Exception as e:
        files_path = ""
        db_logger.logger.error(f"Error while getting files path for chat {chat_id}")
        db_logger.logger.exception(e)
        raise ChatPathError(chat_id) from e
    return files_path


async def close_db():
    try:
        db.close()
        db_logger.logger.info(f"Closed database")
    except Exception as e:
        db_logger.logger.error(f"Error while closing database")
        db_logger.logger.exception(e)
        raise DBClosingError() from e


# username
# last_name
# first_name
