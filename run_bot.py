import telebot
import os
from dotenv import load_dotenv

from chatbot.chatbot import DocumentSearchBot


load_dotenv()
bot = telebot.TeleBot(os.getenv('CHATBOT_KEY'))
ds_bot = DocumentSearchBot()
find_info = ds_bot.get_button_find_info()
load_file = ds_bot.get_button_load_file()
help = ds_bot.get_button_help()
clean = ds_bot.get_button_clean()


@bot.message_handler(commands=['start'])
def handle_start(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_info = telebot.types.KeyboardButton(text=find_info)
    button_import = telebot.types.KeyboardButton(text=load_file)
    button_help = telebot.types.KeyboardButton(text=help)
    button_clean = telebot.types.KeyboardButton(text=clean)
    keyboard.row(button_info, button_import)
    keyboard.row(button_help, button_clean)

    ds_bot.restart(message.chat.id)
    bot.send_message(message.chat.id,
                     ds_bot.get_start_info(),
                     parse_mode='Markdown',
                     reply_markup=keyboard)


@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id,
                     ds_bot.get_help_info(),
                     parse_mode='Markdown')


@bot.message_handler(commands=['clean'])
def handle_clean(message):
    ds_bot.clean_user_dir()
    bot.send_message(message.chat.id,
                     ds_bot.get_clean_info(),
                     parse_mode='Markdown')


@bot.message_handler(content_types=['text'])
def handle_message(message):
    if message.text == find_info:
        bot.send_message(message.chat.id,
                         ds_bot.get_find_message())
    elif message.text == load_file:
        bot.send_message(message.chat.id,
                         ds_bot.load_file_response())
    elif message.text == help:
        handle_help(message)
    elif message.text == clean:
        handle_clean(message)
    else:
        answer = ds_bot.ask(message.text)
        bot.send_message(message.chat.id, answer)


@bot.message_handler(content_types=['document'])
def load_document(message):
    if 'txt' == message.document.file_name.split('.')[1]:
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            bot.send_message(message.chat.id,
                             ds_bot.waiting_for_loading_response())
            try:
                ds_bot.load_file(message.from_user.id,
                                 message.document.file_name, downloaded_file)
                bot.send_message(message.chat.id,
                                 ds_bot.success_file_loading_response())
            except Exception as e:
                bot.send_message(message.chat.id,
                                 ds_bot.loading_file_error_response())
                bot.send_message(message.chat.id, e)
        except Exception as e:
            bot.reply_to(message, e)
    else:
        bot.send_message(ds_bot.error_file_format_response())


def main():
    bot.polling(none_stop=True, interval=0)


if __name__ == '__main__':
    main()
