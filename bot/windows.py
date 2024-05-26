import operator
from aiogram_dialog import Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Multiselect, Column

from bot.states import DeleteFilesForm
from bot.bot import get_data, go_back, list_files, remove_files, CHECKED


file_list_window = Window(
    Const("При необходимости вы можете выбрать файлы для удаления 🗑️:"),
    Column(Multiselect(
        Format(f"{CHECKED}"+" {item[0]}"),
        Format("{item[0]}"),
        id="id_files",
        item_id_getter=operator.itemgetter(1),
        items="files",
    )),
    Button(Const("Удалить выбранные файлы 🗑️"), "b1", on_click=list_files),
    state=DeleteFilesForm.list_files,
    getter=get_data
)

remove_files_window = Window(
    Const("Вы действительно хотите удалить выбранные файлы❓"),
    Button(Const("Да"), "b2", on_click=remove_files),
    Button(Const("Нет"), "b3", on_click=go_back),
    state=DeleteFilesForm.remove_files,
)
