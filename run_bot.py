import asyncio
import os
import hashlib
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram_dialog import Dialog
from aiogram_dialog import setup_dialogs

from bot.bot import router, bot_logger
from bot.commands import set_commands
from bot.windows import file_list_window, remove_files_window
from database.database import create_database, create_admin, close_db
from database.errors import DBCreationError


async def start():
    load_dotenv()
    bot = Bot(os.getenv('CHATBOT_KEY'))
    info = await bot.get_me()
    try:
        await create_database()
        psw = os.getenv('ADM_PSW')
        await create_admin(hashlib.md5(psw.encode('utf-8')).hexdigest())
        bot_logger.logger.info(f"Created database.")
    except DBCreationError as e:
        bot_logger.logger.warning(f"Error occurred while creating database.")
        bot_logger.logger.exception(e)
    except Exception as e:
        await close_db()
        bot_logger.logger.exception(e)
        bot_logger.logger.critical(f"Closed db connection.")

    dp = Dispatcher()
    dp.include_router(router)
    dialog = Dialog(file_list_window, remove_files_window)
    dp.include_router(dialog)
    setup_dialogs(dp)
    await set_commands(bot)
    try:
        bot_logger.logger.info(f"Started bot @{info.username} id={bot.id}.")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        bot_logger.logger.critical(f"Closed bot @{info.username} id={bot.id}.")
        close_db()

if __name__ == "__main__":
    try:
        asyncio.run(start())
    except KeyboardInterrupt:
        print("\nOkay, I'm stopping...")
    finally:
        bot_logger.logger.critical("Bot stopped.")
