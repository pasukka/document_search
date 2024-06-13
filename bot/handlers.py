import hashlib
from aiogram import Bot, types, F
from aiogram.types import ContentType, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from aiogram_dialog import StartMode
from aiogram_dialog import DialogManager

from bot.bot import router, ds_controller, bot_logger
from bot.states import CallBackForm, DeleteFilesForm, DebugForm
from bot.keyboards import reply_keyboard, cancel_inline_keyboard
from bot.utils import download_docs
from database.database import create_chat
from database.errors import ChatCreationError


@router.message(Command("start"))
async def handle_start(message: types.Message):
    id = message.chat.id
    bot_logger.info(f"Chat: {id} - Started bot.")
    try:
        await message.answer(ds_controller.metadata["info"]["start_info"].replace("_", "\\_"),
                             parse_mode='Markdown',
                             reply_markup=reply_keyboard)
        await ds_controller.restart(id)
        user_dir_path = ds_controller.make_user_dir(id)
        await create_chat(id, message.chat.type, user_dir_path)
        bot_logger.info(f"Chat: {id} - Created chat.")
    except ChatCreationError as e:
        bot_logger.warning(
            f"Chat: {id} - Error occurred while creating chat.")
        bot_logger.exception(e)
    except Exception as e:
        bot_logger.exception(e)


@router.message(Command("help"))
async def handle_help(message: types.Message):
    bot_logger.info(f"Chat: {message.chat.id} - Showing help info.")
    await message.answer(ds_controller.metadata["info"]["help_info"].replace("_", "\\_"), parse_mode='Markdown')


@router.message(Command("clean"))
async def handle_clean(message: types.Message):
    await message.answer(ds_controller.metadata["response"]["deleting_file_response"],
                         parse_mode='Markdown')
    user_dir = await ds_controller.clean_user_dir(message.chat.id)
    bot_logger.info(
        f"Chat: {message.chat.id} - Cleaned history and files in folder {user_dir}.")
    await message.answer(ds_controller.metadata["info"]["clean_info"],
                         parse_mode='Markdown')


@router.message(Command("docs_list"))
async def handle_docs_list(message: types.Message, dialog_manager: DialogManager):
    if ds_controller.docs_path == ds_controller.doc_searcher.docs_path:
        await message.answer(f"Используйте /my_docs, чтобы перейти к вашей папке")
        bot_logger.info(f"Chat: {message.chat.id} - Not user's dir.")
    else:
        bot_logger.info(
            f"Chat: {message.chat.id} - Making dialog for showing files list.")
        docs_list = await ds_controller.get_docs_list(message.chat.id)
        await message.answer(f"Количество файлов: *{len(docs_list)}*",
                             parse_mode='Markdown')
        await dialog_manager.start(DeleteFilesForm.list_files, mode=StartMode.RESET_STACK)


@router.message(Command("my_docs"))
async def handle_search(message: types.Message):
    chat_id = message.chat.id
    bot_logger.info(f"Chat: {chat_id} - Search by user's documents.")
    res = await ds_controller.change_docs_path(chat_id)
    if res:
        await message.answer(ds_controller.metadata["response"]["search_response"])
    else:
        await message.answer(ds_controller.metadata["response"]["no_search_response"])


@router.callback_query(F.data.in_(['cancel']))
async def cancel(call: CallbackQuery, state: FSMContext):
    bot_logger.info(
        f"Chat: {call.message.chat.id} - Canceled sending callback or switching to debug mode.")
    await call.message.answer(ds_controller.metadata["response"]["cancelling_response"],
                              parse_mode='Markdown')
    await state.clear()


@router.message(F.content_type == ContentType.TEXT, Command("callback"))
async def handle_callback(message: types.Message, state: FSMContext):
    bot_logger.info(f"Chat: {message.chat.id} - Handelling callback.")
    await state.set_state(CallBackForm.GET_CALLBACK)
    await message.answer(ds_controller.metadata["response"]["write_callback_response"],
                         reply_markup=cancel_inline_keyboard)


@router.message(StateFilter(CallBackForm.GET_CALLBACK))
async def write_callback(message: types.Message, state: FSMContext):
    id = ds_controller.callback(message.chat.id, message.text)
    bot_logger.info(f"Chat: {message.chat.id} - Got callback: id={id}.")
    await message.answer(ds_controller.metadata["response"]["callback_response"])
    await state.clear()


@router.message(StateFilter(DebugForm.password))
async def checking_psw(message: types.Message, state: FSMContext):
    psw = hashlib.md5(str(message.text).encode('utf-8')).hexdigest()
    chat_id = message.chat.id
    bot_logger.info(f"Chat: {chat_id} - Got password.")
    right_psw = await ds_controller.check_psw(chat_id, psw)
    if right_psw:
        bot_logger.info(
            f"Chat: {chat_id} - Right password. Switching to debug mode")
        await message.answer("Переключаемся на модуль разработчика")
        ds_controller.switch_to_debug()
    else:
        bot_logger.info(f"Chat: {chat_id} - Wrong password.")
        await message.answer("Пароль неверен.")
    await state.clear()


@router.message(F.content_type == ContentType.TEXT, Command("debug_mode"))
async def handle_debug_mode(message: types.Message, state: FSMContext):
    bot_logger.info(
        f"Chat: {message.chat.id} - Asking for debug mode password.")
    await message.answer("Введите пароль", reply_markup=cancel_inline_keyboard)
    await state.set_state(DebugForm.password)


@router.message(F.content_type == ContentType.DOCUMENT)
async def handle_document(message: types.Message, bot: Bot):
    file_name = message.document.file_name
    if 'txt' == file_name.split('.')[1]:
        try:
            await download_docs(message, bot, file_name)
        except Exception as e:
            bot_logger.error(
                f"Chat: {message.chat.id} - Error occurred: {e}.")
            bot_logger.exception(e)
            await message.reply(message, e)
    else:
        bot_logger.warning(
            f"Chat: {message.chat.id} - Wrong file format.")
        await message.answer(ds_controller.metadata["error"]["error_file_format"])


@router.message()
async def handle_message(message: types.Message):
    if message.text == "🔍 Найти информацию":
        bot_logger.info(f"Chat: {message.chat.id} - Button find info.")
        await message.answer(ds_controller.metadata["response"]["find_response"])
    elif message.text == "📤 Загрузить файл":
        bot_logger.info(f"Chat: {message.chat.id} - Button load file.")
        await message.answer(ds_controller.metadata["response"]["load_file_response"])
    elif message.text == "🆘 Помощь":
        bot_logger.info(f"Chat: {message.chat.id} - Button help.")
        await handle_help(message)
    elif message.text == "🧹 Очистить историю":
        bot_logger.info(f"Chat: {message.chat.id} - Button clear.")
        await handle_clean(message)
    else:
        bot_logger.info(f"Chat: {message.chat.id} - Got text message.")
        answer = ds_controller.ask(message.text, message.chat.id)
        bot_logger.info(f"Chat: {message.chat.id} - Found info.")
        await message.answer(answer)
