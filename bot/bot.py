from aiogram import Router

from bot.search_manager import DocumentSearcherManager

CHECKED = '✅'

router = Router()
ds_controller = DocumentSearcherManager()
bot_logger = ds_controller.bot_logger
