import pytest

from aiogram import types, Dispatcher
from bot.bot import handle_start, ds_controller
from database.database import create_database, close_db

async def echo(message: types.Message):
    await message.answer(message.text)

def setup(dp: Dispatcher):
    dp.register_message_handler(echo)


class MockMessage:
    def __init__(self, text, chat_id):
        self.text = text
        self.chat = types.Chat(id=chat_id, type='private')
        self._answer = ""

    async def answer(self, text: str, parse_mode, reply_markup):
        self._answer = text


@pytest.mark.asyncio
async def test_echo_handler():
    text_mock = "/start"
    await create_database()
    message_mock = MockMessage(text=text_mock, chat_id=1223)
    await handle_start(message=message_mock)
    assert message_mock._answer == ds_controller.metadata["info"]["start_info"].replace("_", "\\_")
    await close_db()

