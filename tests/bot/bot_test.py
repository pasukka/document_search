import pytest

from aiogram import types
from bot.handlers import handle_start, handle_help, handle_clean, handle_docs_list, ds_controller
from database.database import create_database, close_db


class MockMessage:
    def __init__(self, text, chat_id):
        self.text = text
        self.chat = types.Chat(id=chat_id, type='private')
        self.answers = []

    async def answer(self, text: str, parse_mode='', reply_markup=''):
        self.answers.append(text)


@pytest.mark.asyncio
async def test_start():
    text_mock = "/start"
    await create_database()
    message_mock = MockMessage(text=text_mock, chat_id=1223)
    await handle_start(message=message_mock)
    assert message_mock.answers[0] == ds_controller.metadata["info"]["start_info"].replace(
        "_", "\\_")
    await close_db()


@pytest.mark.asyncio
async def test_help():
    text_mock = "/help"
    await create_database()
    message_mock = MockMessage(text=text_mock, chat_id=1223)
    await handle_help(message=message_mock)
    assert message_mock.answers[0] == ds_controller.metadata["info"]["help_info"].replace(
        "_", "\\_")
    await close_db()


@pytest.mark.asyncio
async def test_clean():
    text_mock = "/clean"
    await create_database()
    message_mock = MockMessage(text=text_mock, chat_id=1223)
    await handle_clean(message=message_mock)
    assert message_mock.answers[0] == ds_controller.metadata["response"]["deleting_file_response"]
    assert message_mock.answers[1] == ds_controller.metadata["info"]["clean_info"]
    await close_db()


# @pytest.mark.asyncio
# async def test_clean():
#     text_mock = "/docs_list"
#     await create_database()
#     message_mock = MockMessage(text=text_mock, chat_id=1223)
#     await handle_docs_list(message=message_mock)
#     assert message_mock.answers[0] == f"Количество файлов: *{len(docs_list)}*"
#     await close_db()
