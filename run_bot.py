import telebot
import os
import time
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
    ds_bot.restart()
    bot.send_message(message.chat.id,
                     ds_bot.get_info(),
                     parse_mode='Markdown',
                     reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
def handle_message(message):
    if message.text == FIND_INFO:
        bot.send_message(message.chat.id,
                         ds_bot.get_answer_message())
    elif message.text == LOAD_FILE:
        bot.send_message(message.chat.id,
                         'Жду загрузку файла!')
    else:
        try:
            answer = ds_bot.ask(message.text)
            bot.send_message(message.chat.id,
                             answer)
        except ValueError:
            bot.send_message(message.chat.id,
                             'Возникла ошибка. Повторите запрос позже.')
        except TimeoutError:
            time.sleep(2)
            handle_message(message)
        except Exception as e:
            bot.send_message(message.chat.id,
                             'Возникла ошибка. Повторите запрос еще раз.')
            pass


@bot.message_handler(content_types=['document'])
def load(message):
    if 'txt' == message.document.file_name.split('.')[1]:
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            try:
                bot.send_message(message.chat.id,
                                'Подождите, я загружаю файл...')
                ds_bot.load_file(message.document.file_name, downloaded_file)
                bot.send_message(message.chat.id,
                                'Загрузка прошла успешно!')
            except Exception as e:
                bot.send_message(message.chat.id,
                             'Загрузка прервана!')
                bot.send_message(message.chat.id, e)
        except Exception as e:
            bot.reply_to(message, e)

        # TODO: MAKE check for TimeoutError everywhere and Huggingface tokens
    else:
        bot.send_message("Неправильный формат файла")


def main():
    bot.polling(none_stop=True, interval=0)


if __name__ == '__main__':
    main()
