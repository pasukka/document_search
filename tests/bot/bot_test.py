import pytest
from unittest.mock import AsyncMock

from bot.bot import handle_start, ds_controller
from bot.keyboards import reply_keyboard


@pytest.mark.asyncio
async def test_start():
    message = AsyncMock()
    await handle_start(message)

    message.answer.assert_called_with(ds_controller.metadata["info"]["start_info"].replace(
        "_", "\\_"), reply_markup=reply_keyboard)


'''
TODO

https://www.youtube.com/watch?v=w0l4S838Idc

https://dev.to/blueset/how-to-write-integration-tests-for-a-telegram-bot-4c0e

'''
