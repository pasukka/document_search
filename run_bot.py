import asyncio
import logging
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from chatbot.bot import router
from chatbot.commands import set_commands

async def start():
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    bot = Bot(os.getenv('CHATBOT_KEY'))
    dp = Dispatcher()
    dp.include_router(router)
    await set_commands(bot)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(start())
