from aiogram.fsm.state import StatesGroup, State


class CallBackForm(StatesGroup):
    GET_CALLBACK = State()


class DebugForm(StatesGroup):
    password = State()


class DeleteFilesForm(StatesGroup):
    list_files = State()
    remove_files = State()
