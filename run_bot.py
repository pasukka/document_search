import asyncio
import logging
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ContentType
from aiogram.filters.command import Command

from chatbot.chatbot import DocumentSearchBot

# TODO: make /smth - some responses of what is wrong

load_dotenv()
logging.basicConfig(level=logging.INFO)
bot = Bot(os.getenv('CHATBOT_KEY'))
dp = Dispatcher()

ds_bot = DocumentSearchBot()
find_info = ds_bot.get_button_find_info()
load_file = ds_bot.get_button_load_file()
help = ds_bot.get_button_help()
clean = ds_bot.get_button_clean()


@dp.message(Command("start"))
async def handle_start(message: types.Message):
    kb = [
        [types.KeyboardButton(text=find_info),
        types.KeyboardButton(text=load_file)],
        [types.KeyboardButton(text=help),
        types.KeyboardButton(text=clean)]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb,
                                         resize_keyboard=True)

    await message.answer(ds_bot.get_start_info(),
                         parse_mode='Markdown',
                         reply_markup=keyboard)
    ds_bot.restart(message.chat.id)

@dp.message(Command("help"))
async def handle_help(message: types.Message):
    await message.answer(ds_bot.get_help_info(),
                         parse_mode='Markdown')
    
@dp.message(Command("clean"))
async def handle_clean(message: types.Message):
    await message.answer(ds_bot.get_clean_info(),
                         parse_mode='Markdown')

@dp.message(F.content_type == ContentType.DOCUMENT)
async def handle_message(message: types.Message):
    if 'txt' == message.document.file_name.split('.')[1]:
        try:
            file_info = await bot.get_file(message.document.file_id)
            await message.answer(ds_bot.waiting_for_loading_response())
            try:
                path = ds_bot.get_path(message.chat.id)
                await bot.download_file(file_info.file_path, path + message.document.file_name)
                ds_bot.change_docs_path(message.chat.id)
                await message.answer(ds_bot.success_file_loading_response())
            except Exception as e:
                await message.answer(ds_bot.loading_file_error_response())

        except Exception as e:
            message.reply(message, e)
    else:
        await message.answer(ds_bot.error_file_format_response())

@dp.message()
async def handle_message(message: types.Message):
    if message.text == find_info:
        await message.answer(ds_bot.get_find_message())
    elif message.text == load_file:
        await message.answer(ds_bot.load_file_response())
    elif message.text == help:
        handle_help(message)
    elif message.text == clean:
        handle_clean(message)
    else:
        answer = ds_bot.ask(message.text)
        await message.answer(answer)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
