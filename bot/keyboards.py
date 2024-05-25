from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

reply_keyboard = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(
            text="🔍 Найти информацию",
        ),
        KeyboardButton(
            text="📤 Загрузить файл",
        ),
    ],
    [
        KeyboardButton(
            text="🆘 Помощь",
        ),
        KeyboardButton(
            text="🧹 Очистить историю",
        ),
    ]
],
    resize_keyboard=True)


cancel_inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='⛔ Отмена',
            callback_data="cancel"
        )
    ]
])
