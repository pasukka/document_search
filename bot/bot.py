from aiogram import Bot, types, F, Router
from aiogram.types import ContentType, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from aiogram_dialog import StartMode
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

from bot.states import CallBackForm, DeleteFilesForm
from bot.keyboards import reply_keyboard, cancel_inline_keyboard
from bot.search_manager import DocumentSearcherManager
from database.database import create_chat

CHECKED = '✅'

router = Router()
ds_controller = DocumentSearcherManager()
bot_logger = ds_controller.bot_logger


@router.callback_query(F.data.in_(['cancel']))
async def cancel(call: CallbackQuery, state: FSMContext):
    bot_logger.logger.info(
        f"Chat: {call.message.chat.id} - Canceled callback sending.")
    answer = ds_controller.metadata["response"]["cancelling_callback_response"]
    await call.message.answer(answer, parse_mode='Markdown')
    await call.answer()
    await state.clear()


async def remove_files(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    message = dialog_manager.event.message
    await message.answer(ds_controller.metadata["response"]["deleting_file_response"],
                         parse_mode='Markdown')
    files = dialog_manager.dialog_data["files_list"]
    chat_id = message.chat.id
    user_dir = await ds_controller.remove_chosen_files(chat_id, files)
    bot_logger.logger.info(
        f"Chat: {message.chat.id} - Removed files from folder {user_dir}.")
    await message.answer(ds_controller.metadata["info"]["clean_info"],
                         parse_mode='Markdown')
    await dialog_manager.done()


@router.message(Command("help"))
async def handle_help(message: types.Message):
    bot_logger.logger.info(f"Chat: {message.chat.id} - Showing help info.")
    await message.answer(ds_controller.metadata["info"]["help_info"].replace("_", "\\_"), parse_mode='Markdown')


async def list_files(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    message = dialog_manager.event.message
    bot_logger.logger.info(
        f"Chat: {message.chat.id} - Chose files to be removed.")
    buttons = message.reply_markup.inline_keyboard
    files = [row[0].text.replace(CHECKED, '').replace(' ', '')
             for row in buttons if row[0].text.startswith(CHECKED)]
    dialog_manager.dialog_data["files_list"] = files
    await dialog_manager.switch_to(DeleteFilesForm.remove_files)


async def get_data(**kwargs):
    id = kwargs['event_context'].chat.id
    docs_list = await ds_controller.get_docs_list(id)
    bot_logger.logger.info(f"Chat: {id} - Showing files list.")
    id = 1
    files = []
    for data in docs_list:
        files.append((data, str(id)))
        id += 1
    return {
        "files": files,
        "count": len(files),
    }


async def go_back(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    bot_logger.logger.info(
        f"Chat: {dialog_manager.event.message.chat.id} - Back in dialog message.")
    await dialog_manager.back()


@router.message(Command("docs_list"))
async def handle_docs_list(message: types.Message, dialog_manager: DialogManager):
    bot_logger.logger.info(
        f"Chat: {message.chat.id} - Making dialog for showing files list.")
    docs_list = await ds_controller.get_docs_list(message.chat.id)
    await message.answer(f"Количество файлов: *{len(docs_list)}*",
                         parse_mode='Markdown')
    await dialog_manager.start(DeleteFilesForm.list_files, mode=StartMode.RESET_STACK)


@router.message(Command("start"))
async def handle_start(message: types.Message):
    id = message.chat.id
    bot_logger.logger.info(f"Chat: {id} - Started bot.")
    await message.answer(ds_controller.metadata["info"]["start_info"],
                         parse_mode='Markdown',
                         reply_markup=reply_keyboard)
    await ds_controller.restart(id)
    user_dir_path = ds_controller.make_user_dir(id)
    await create_chat(id, message.chat.type, user_dir_path)


@router.message(Command("clean"))
async def handle_clean(message: types.Message):
    await message.answer(ds_controller.metadata["response"]["deleting_file_response"],
                         parse_mode='Markdown')
    user_dir = await ds_controller.clean_user_dir(message.chat.id)
    bot_logger.logger.info(
        f"Chat: {message.chat.id} - Cleaned history and files in folder {user_dir}.")
    await message.answer(ds_controller.metadata["info"]["clean_info"],
                         parse_mode='Markdown')


@router.message(StateFilter(CallBackForm.GET_CALLBACK))
async def write_callback(message: types.Message, state: FSMContext):
    id = ds_controller.callback(message.chat.id, message.text)
    bot_logger.logger.info(f"Chat: {message.chat.id} - Got callback: id={id}.")
    await message.answer(ds_controller.metadata["response"]["callback_response"])
    await state.clear()


@router.message(F.content_type == ContentType.TEXT, Command("callback"))
async def handle_callback(message: types.Message, state: FSMContext):
    bot_logger.logger.info(f"Chat: {message.chat.id} - Handelling callback.")
    await state.set_state(CallBackForm.GET_CALLBACK)
    await message.answer(ds_controller.metadata["response"]["write_callback_response"],
                         reply_markup=cancel_inline_keyboard)


@router.message(F.content_type == ContentType.DOCUMENT)
async def handle_message(message: types.Message, bot: Bot):
    file_name = message.document.file_name
    if 'txt' == file_name.split('.')[1]:
        try:
            file_info = await bot.get_file(message.document.file_id)
            bot_logger.logger.info(
                f"Chat: {message.chat.id} - Got file in chat.")
            await message.answer(ds_controller.metadata["response"]["loading_file_response"].replace("{file}", f"*{file_name}*"),
                                 parse_mode='Markdown')
            try:
                path = await ds_controller.get_path(message.chat.id)
                await bot.download_file(file_info.file_path, path + file_name)
                bot_logger.logger.info(
                    f"Chat: {message.chat.id} - Downloaded file {file_name} to path: {path}.")
                await ds_controller.change_docs_path(message.chat.id)
                await message.answer(ds_controller.metadata["response"]["file_loaded_response"].replace("{file}", f"*{file_name}*"),
                                     parse_mode='Markdown')
            except Exception as e:
                bot_logger.logger.error(
                    f"Chat: {message.chat.id} - Error while loading file {file_name}.")
                bot_logger.logger.exception(e)
                await message.answer(ds_controller.metadata["error"]["loading_file_error"])
        except Exception as e:
            bot_logger.logger.error(
                f"Chat: {message.chat.id} - Error occurred: {e}.")
            bot_logger.logger.exception(e)
            await message.reply(message, e)
    else:
        bot_logger.logger.warning(
            f"Chat: {message.chat.id} - Wrong file format.")
        await message.answer(ds_controller.metadata["error"]["error_file_format"])


@router.message()
async def handle_message(message: types.Message):
    if message.text == "🔍 Найти информацию":
        bot_logger.logger.info(f"Chat: {message.chat.id} - Button find info.")
        await message.answer(ds_controller.metadata["response"]["find_response"])
    elif message.text == "📤 Загрузить файл":
        bot_logger.logger.info(f"Chat: {message.chat.id} - Button load file.")
        await message.answer(ds_controller.metadata["response"]["load_file_response"])
    elif message.text == "🆘 Помощь":
        bot_logger.logger.info(f"Chat: {message.chat.id} - Button help.")
        await handle_help(message)
    elif message.text == "🧹 Очистить историю":
        bot_logger.logger.info(f"Chat: {message.chat.id} - Button clear.")
        await handle_clean(message)
    else:
        bot_logger.logger.info(f"Chat: {message.chat.id} - Got text message.")
        answer = ds_controller.ask(message.text, message.chat.id)
        bot_logger.logger.info(f"Chat: {message.chat.id} - Found info.")
        await message.answer(answer)
