from aiogram.types import CallbackQuery

from aiogram import Bot, types, F, Router
from aiogram.types import ContentType
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from bot.states import CallBackForm
from bot.keyboards import reply_keyboard, cancel_inline_keyboard
from bot.search_manager import DocumentSearcherManager

router = Router()
ds_controller = DocumentSearcherManager()


@router.callback_query(F.data.in_(['cancel']))
async def cancel(call: CallbackQuery, state: FSMContext):
    answer = ds_controller.metadata["response"]["cancelling_callback_response"]
    await call.message.answer(answer, parse_mode='Markdown')
    await call.answer()
    await state.clear()


@router.message(Command("help"))
async def handle_help(message: types.Message):
    await message.answer(ds_controller.metadata["info"]["help_info"].replace("_", "\\_"), parse_mode='Markdown')


@router.message(Command("docs_list"))
async def handle_docs_list(message: types.Message):
    docs_list = ds_controller.get_docs_list(message.chat.id)
    docs_string = "\n".join(docs_list)
    docs_string += f"\nКоличество файлов: {len(docs_list)}"
    await message.answer(docs_string)


@router.message(Command("start"))
async def handle_start(message: types.Message):
    await message.answer(ds_controller.metadata["info"]["start_info"],
                         parse_mode='Markdown',
                         reply_markup=reply_keyboard)
    ds_controller.restart(message.chat.id)


@router.message(Command("clean"))
async def handle_clean(message: types.Message):
    ds_controller.clean_user_dir(chat_id=message.chat.id)
    await message.answer(ds_controller.metadata["info"]["clean_info"],
                         parse_mode='Markdown')


@router.message(StateFilter(CallBackForm.GET_CALLBACK))
async def write_callback(message: types.Message, state: FSMContext):
    ds_controller.callback(message.text)
    await message.answer(ds_controller.metadata["response"]["callback_response"])
    await state.clear()


@router.message(F.content_type == ContentType.TEXT, Command("callback"))
async def handle_callback(message: types.Message, state: FSMContext):
    await state.set_state(CallBackForm.GET_CALLBACK)
    await message.answer(ds_controller.metadata["response"]["write_callback_response"],
                         reply_markup=cancel_inline_keyboard)


@router.message(F.content_type == ContentType.DOCUMENT)
async def handle_message(message: types.Message, bot: Bot):
    if 'txt' == message.document.file_name.split('.')[1]:
        try:
            file_info = await bot.get_file(message.document.file_id)
            await message.answer(ds_controller.metadata["response"]["loading_file_response"])
            try:
                path = ds_controller.get_path(message.chat.id)
                await bot.download_file(file_info.file_path, path + message.document.file_name)
                ds_controller.change_docs_path(message.chat.id)
                await message.answer(ds_controller.metadata["response"]["file_loaded_response"])
            except Exception as e:
                await message.answer(ds_controller.metadata["error"]["loading_file_error"])
                print(e)
        except Exception as e:
            await message.reply(message, e)
    else:
        await message.answer(ds_controller.metadata["error"]["error_file_format"])


@router.message()
async def handle_message(message: types.Message):
    if message.text == "🔍 Найти информацию":
        await message.answer(ds_controller.metadata["response"]["find_response"])
    elif message.text == "📤 Загрузить файл":
        await message.answer(ds_controller.metadata["response"]["load_file_response"])
    elif message.text == "🆘 Помощь":
        await handle_help(message)
    elif message.text == "🧹 Очистить историю":
        await handle_clean(message)
    else:
        answer = ds_controller.ask(message.text)
        await message.answer(answer)
