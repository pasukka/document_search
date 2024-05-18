import telebot
import os
from dotenv import load_dotenv

load_dotenv()
bot = telebot.TeleBot(os.getenv('CHATBOT_KEY'))


# keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
# button_import = telebot.types.KeyboardButton(text="Загрузить файлы")
# button_info = telebot.types.KeyboardButton(text="Найти информацию")
# keyboard.add(button_import)
# keyboard.add(button_info)

class DocumentSearchBot:

    @bot.message_handler(commands=['start'])
    def handle_start(message):
        bot.send_message(
            message.chat.id, 'Добро пожаловать в бот для поиска информации по документу')  # reply_markup=keyboard

    @bot.message_handler(content_types=['text'])
    def handle_message(message):
        # if message.text == 'Найти информацию':
        bot.send_message(message.chat.id, f'Yep!')

    def start(self):
        bot.polling(none_stop=True, interval=0)
