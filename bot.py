import os
import telebot
from dotenv import load_dotenv
from utils.ai import predict
from googletrans import Translator
from telebot import types
from dataclasses import dataclass
from telebot.types import CallbackQuery


load_dotenv()
BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)
translator = Translator()
settings_by_chat_id = {}


@dataclass()
class ChatSettings:
    delete_flag: bool = True
    toxic_rate: float = 0.7

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    settings = ChatSettings()
    settings_by_chat_id[message.chat.id] = settings_by_chat_id.get(message.chat.id, settings)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Settings")
    markup.add(btn1)
    bot.reply_to(message, "Bot started", reply_markup=markup)

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    chat_id = message.chat.id
    chat_settings = settings_by_chat_id[chat_id]
    if message.text == 'Settings':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Delete toxic messages?')
        markup.add(btn1)
        bot.send_message(message.from_user.id, 'Choose button', reply_markup=markup)
    elif message.text == 'Delete toxic messages?':
        bot.send_message(message.chat.id, "Delete toxic messages?", reply_markup=gen_markup())
    else:
        text = translator.translate(message.text).text
        prob = predict(text)[0][1]
        if prob > chat_settings.toxic_rate:
            if chat_settings.delete_flag:
                bot.delete_message(chat_id, message.message_id)
                bot.send_message(chat_id, 'Your message has been detected as toxic. (' + str(prob) + ')')
            else:
                bot.reply_to(message, 'Your message has been detected as toxic. (' + str(prob) + ')')
        else:
            bot.reply_to(message, prob)


bot.infinity_polling()
