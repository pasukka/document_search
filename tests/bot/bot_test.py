import pytest
from aiogram import types
from aiogram_dialog import StartMode

from bot import handlers
from bot.bot import ds_controller
from database.database import create_database, close_db
from bot.states import CallBackForm, DeleteFilesForm


class MockBot:
    def download_file(self):
        pass


class MockDocument:
    def __init__(self, file_name):
        self.file_name = file_name


class MockMessage:
    document: MockDocument

    def __init__(self, text, chat_id):
        self.text = text
        self.chat = types.Chat(id=chat_id, type='private')
        self.answers = []

    async def answer(self, text: str, parse_mode='', reply_markup=''):
        self.answers.append(text)


class MockState:
    async def set_state(self, state):
        self.state = state

    async def clear(self):
        pass


class MockCall:
    def __init__(self, message: MockMessage):
        self.message = message


class MockDialogManager:
    async def start(self, state, mode):
        self.state = state
        self.mode = mode


@pytest.mark.asyncio
async def test_start():
    text_mock = "/start"
    await create_database()
    message_mock = MockMessage(text=text_mock, chat_id=1223)
    await handlers.handle_start(message=message_mock)
    assert message_mock.answers[0] == ds_controller.metadata["info"]["start_info"].replace(
        "_", "\\_")
    await close_db()


@pytest.mark.asyncio
async def test_help():
    text_mock = "/help"
    await create_database()
    message_mock = MockMessage(text=text_mock, chat_id=1223)
    await handlers.handle_help(message=message_mock)
    assert message_mock.answers[0] == ds_controller.metadata["info"]["help_info"].replace(
        "_", "\\_")
    await close_db()


@pytest.mark.asyncio
async def test_clean():
    text_mock = "/clean"
    await create_database()
    message_mock = MockMessage(text=text_mock, chat_id=1223)
    await handlers.handle_clean(message=message_mock)
    assert message_mock.answers[0] == ds_controller.metadata["response"]["deleting_file_response"]
    assert message_mock.answers[1] == ds_controller.metadata["info"]["clean_info"]
    await close_db()


@pytest.mark.asyncio
async def test_docs_list():
    text_mock = "/docs_list"
    await create_database()
    message_mock = MockMessage(text=text_mock, chat_id=1223)
    manager_mock = MockDialogManager()
    await handlers.handle_docs_list(message=message_mock, dialog_manager=manager_mock)
    assert message_mock.answers[0] == f"Количество файлов: *0*"
    assert manager_mock.state == DeleteFilesForm.list_files
    assert manager_mock.mode == StartMode.RESET_STACK
    await close_db()


@pytest.mark.asyncio
async def test_my_docs():
    text_mock = "/my_docs"
    await create_database()
    message_mock = MockMessage(text=text_mock, chat_id=1223)
    await handlers.handle_search(message=message_mock)
    assert message_mock.answers[0] == ds_controller.metadata["response"]["no_search_response"]
    await close_db()


@pytest.mark.asyncio
async def test_callback():
    text_mock = "/callback"
    message_mock = MockMessage(text=text_mock, chat_id=1223)
    state = MockState()
    await create_database()
    await handlers.handle_callback(message=message_mock, state=state)
    assert message_mock.answers[0] == ds_controller.metadata["response"]["write_callback_response"]
    new_state = state.state
    assert new_state == CallBackForm.GET_CALLBACK

    text_mock = "some user error"
    message_mock = MockMessage(text=text_mock, chat_id=1223)
    await handlers.write_callback(message=message_mock, state=state)
    assert message_mock.answers[0] == ds_controller.metadata["response"]["callback_response"]
    await close_db()


@pytest.mark.asyncio
async def test_cancel():
    text_mock = ""
    message_mock = MockMessage(text=text_mock, chat_id=1223)
    state = MockState()
    call = MockCall(message_mock)
    await create_database()
    await handlers.cancel(call=call, state=state)
    assert message_mock.answers[0] == ds_controller.metadata["response"]["cancelling_response"]
    await close_db()


@pytest.mark.asyncio
async def debug_mode():
    text_mock = "/debug_mode"
    message_mock = MockMessage(text=text_mock, chat_id=1223)
    state = MockState()
    await create_database()
    await handlers.handle_debug_mode(message=message_mock, state=state)
    assert message_mock.answers[0] == "Введите пароль"
    await close_db()


@pytest.mark.asyncio
async def debug_mode():
    text_mock = "/debug_mode"
    message_mock = MockMessage(text=text_mock, chat_id=1223)
    bot = MockBot()
    doc = MockDocument("file")
    message_mock.document(doc)
    await create_database()
    await handlers.handle_document(message=message_mock, bot=bot)
    assert message_mock.answers[0] == ds_controller.metadata["error"]["error_file_format"]
    doc.file_name = "file.txt"
    await handlers.handle_document(message=message_mock, bot=bot)
    assert message_mock.answers[0] == ds_controller.metadata["response"]["loading_file_response"].replace(
        "{file}", f"*{doc.file_name}*")
    assert message_mock.answers[0] == ds_controller.metadata["response"]["file_loaded_response"].replace(
        "{file}", f"*{doc.file_name}*")
    await close_db()


@pytest.mark.asyncio
async def debug_mode():
    text_mock = "🔍 Найти информацию"
    message_mock = MockMessage(text=text_mock, chat_id=1223)
    await create_database()
    await handlers.handle_message(message=message_mock)
    assert message_mock.answers[0] == ds_controller.metadata["response"]["find_response"]

    message_mock.text = "📤 Загрузить файл"
    await handlers.handle_message(message=message_mock)
    assert message_mock.answers[0] == ds_controller.metadata["response"]["load_file_response"]
    await close_db()
