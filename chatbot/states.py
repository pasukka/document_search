from aiogram.fsm.state import StatesGroup, State


class CallBackForm(StatesGroup):
    GET_CALLBACK = State()
