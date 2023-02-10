import os
import telebot
from dotenv import load_dotenv
from utils.ai import predict
from googletrans import Translator
from telebot import types
from dataclasses import dataclass
from telebot.types import CallbackQuery
from utils.googlesheets_handler import append_new_cell


load_dotenv()
BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)
translator = Translator()
settings_by_chat_id = {}


@dataclass()
class ChatSettings:
    delete_flag: bool = True
    toxic_rate: float = 0.7
    validate_flag: bool = True


def gen_markup():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(types.InlineKeyboardButton("Yes", callback_data="cb_yes"),
                               types.InlineKeyboardButton("No", callback_data="cb_no"))
    return markup


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call: CallbackQuery):
    chat_id = call.message.chat.id
    chat_settings = settings_by_chat_id[chat_id]
    if call.data == 'toxic':
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.delete_message(call.message.chat.id, call.message.reply_to_message.id)
        bot.send_message(call.message.chat.id, '*Ви позначити повідомлення *' + call.message.reply_to_message.text +
                         '* як токсичне.*', parse_mode="Markdown")
        append_new_cell(True, call.message.reply_to_message.text)
    elif call.data == 'non_toxic':
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.delete_message(call.message.chat.id, call.message.reply_to_message.id)
        bot.send_message(call.message.chat.id, '*Ви позначити повідомлення *' + call.message.reply_to_message.text +
                         '* як не токсичне.*', parse_mode="Markdown")
        append_new_cell(False, call.message.reply_to_message.text)
    elif call.data == "cb_yes":
        bot.answer_callback_query(call.id, "Answer is Yes")
        chat_settings.delete_flag = True
        bot.send_message(chat_id, "Settings updated", reply_markup=gen_base_menu())
    elif call.data == "cb_no":
        bot.answer_callback_query(call.id, "Answer is No")
        chat_settings.delete_flag = False
    bot.send_message(chat_id, "Settings updated", reply_markup=gen_base_menu())

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    settings = ChatSettings()
    settings_by_chat_id[message.chat.id] = settings_by_chat_id.get(message.chat.id, settings)
    bot.reply_to(message, "Bot started", reply_markup=gen_base_menu())


def gen_base_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Settings")
    markup.add(btn1)
    return markup


@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    chat_id = message.chat.id
    chat_settings = settings_by_chat_id[chat_id]
    if message.text == 'Settings':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        btn1 = types.KeyboardButton('Delete toxic messages?')
        markup.add(btn1)
        bot.send_message(message.from_user.id, 'Choose button', reply_markup=markup)
    elif message.text == 'Delete toxic messages?':
        bot.send_message(message.chat.id, "Choose answer", reply_markup=gen_markup())
    else:
        text = translator.translate(message.text).text
        prob = predict(text)[0][1]
        response = ''
        if prob > chat_settings.toxic_rate:
            if chat_settings.delete_flag:
                bot.delete_message(chat_id, message.message_id)
                bot.send_message(chat_id, 'Your message has been detected as toxic. (' + str(prob) + ')')
            else:
                response = 'Your message has been detected as toxic. (' + str(prob) + ')'
        else:
            response = str(prob)
        if chat_settings.validate_flag and len(response)>0:
            val_markup = validation_markup()
            bot.reply_to(message, response, reply_markup=val_markup)
        elif len(response)>0:
            bot.reply_to(message, response)


def validation_markup():
    val_markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton('😡 Toxic', callback_data='toxic')
    button2 = types.InlineKeyboardButton('👌 Not toxic', callback_data='non_toxic')
    val_markup.add(button, button2)
    return val_markup

bot.infinity_polling()
