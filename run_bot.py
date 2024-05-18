import telebot
import os
from dotenv import load_dotenv

from chatbot.chatbot import DocumentSearchBot

FIND_INFO = "Найти информацию"
LOAD_FILE = "Загрузить файл"

load_dotenv()
bot = telebot.TeleBot(os.getenv('CHATBOT_KEY'))
ds_bot = DocumentSearchBot()

keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
button_info = telebot.types.KeyboardButton(text=FIND_INFO)
button_import = telebot.types.KeyboardButton(text=LOAD_FILE)
keyboard.add(button_info)
keyboard.add(button_import)


@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id,
                     ds_bot.get_info(),
                     parse_mode='Markdown',
                     reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
def handle_message(message):
    if message.text == FIND_INFO:
        bot.send_message(message.chat.id, 
                         ds_bot.get_answer_message())
    else:
        answer = ds_bot.ask(message.text)
        bot.send_message(message.chat.id, 
                         answer)

def main():
    bot.polling(none_stop=True, interval=0)


if __name__ == '__main__':
    main()
