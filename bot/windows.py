import operator
from aiogram_dialog import Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Multiselect, Column

from bot.states import DeleteFilesForm
from bot.bot import delete_files, CHECKED


file_list_window = Window(
    Const("При необходимости вы можете выбрать файлы для удаления 🗑️:"),
    Column(Multiselect(
        Format(f"{CHECKED}"+" {item[0]}"),
        Format("{item[0]}"),
        id="id_files",
        item_id_getter=operator.itemgetter(1),
        items="files",
    )),
    Button(Const("Удалить выбранные файлы"), "b2", on_click=delete_files),
    state=DeleteFilesForm.file_delete
)

# TODO: make second window for "do you really want?" back|yes
