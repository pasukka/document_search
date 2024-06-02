from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='start',
            description='запустить бота'
        ),
        BotCommand(
            command='help',
            description='информация по работе с ботом'
        ),
        BotCommand(
            command='docs_list',
            description='список загруженных документов'
        ),
        BotCommand(
            command='my_docs',
            description='поиск по загруженным документам'
        ),
        BotCommand(
            command='clean',
            description='очистить историю документов'
        ),
        BotCommand(
            command='callback',
            description='отправить описание проблемы разработчикам'
        ),
        BotCommand(
            command='debug_mode',
            description='модуль разработчика'
        )
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())
