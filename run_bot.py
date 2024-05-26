import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram_dialog import Dialog
from aiogram_dialog import setup_dialogs

from bot.bot import router, get_data
from bot.commands import set_commands
from bot.windows import file_list_window


async def start():
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    bot = Bot(os.getenv('CHATBOT_KEY'))
    dp = Dispatcher()
    dp.include_router(router)
    dialog = Dialog(file_list_window, getter=get_data)
    dp.include_router(dialog)
    setup_dialogs(dp)
    await set_commands(bot)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(start())
