from aiogram import Bot, types
from aiogram.types import CallbackQuery

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

from bot.states import DeleteFilesForm
from bot.bot import ds_controller, bot_logger, CHECKED


async def go_back(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    bot_logger.logger.info(
        f"Chat: {dialog_manager.event.message.chat.id} - Back in dialog message.")
    await dialog_manager.back()


async def list_files(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    message = dialog_manager.event.message
    bot_logger.logger.info(
        f"Chat: {message.chat.id} - Chose files to be removed.")
    buttons = message.reply_markup.inline_keyboard
    files = [row[0].text.replace(CHECKED, '').replace(' ', '')
             for row in buttons if row[0].text.startswith(CHECKED)]
    dialog_manager.dialog_data["files_list"] = files
    await dialog_manager.switch_to(DeleteFilesForm.remove_files)


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


async def download_docs(message: types.Message, bot: Bot, file_name: str):
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
