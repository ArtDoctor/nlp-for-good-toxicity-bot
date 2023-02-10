import os
import telebot
from dotenv import load_dotenv
from utils.ai import predict
from googletrans import Translator
from telebot import types
from dataclasses import dataclass
from telebot.types import CallbackQuery
from utils.googlesheets_handler import append_new_cell
from utils.markup import gen_yes_no_markup, gen_base_menu, validation_markup

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


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call: CallbackQuery):
    chat_id = call.message.chat.id
    chat_settings = settings_by_chat_id[chat_id]
    if call.data == 'toxic':
        bot.delete_message(chat_id, call.message.id)
        bot.delete_message(chat_id, call.message.reply_to_message.id)
        bot.send_message(chat_id, '*You have marked the message *' + call.message.reply_to_message.text +
                         '* as toxic.*', parse_mode="Markdown")
        append_new_cell(True, call.message.reply_to_message.text)
    elif call.data == 'non_toxic':
        bot.delete_message(chat_id, call.message.id)
        bot.delete_message(chat_id, call.message.reply_to_message.id)
        bot.send_message(chat_id, '*YYou have marked the message *' + call.message.reply_to_message.text +
                         '* as not toxic.*', parse_mode="Markdown")
        append_new_cell(False, call.message.reply_to_message.text)
    elif call.data == "del_yes":
        chat_settings.delete_flag = True
        bot.send_message(chat_id, "Toxic messages will be deleted", reply_markup=gen_base_menu())
    elif call.data == "del_no":
        chat_settings.delete_flag = False
        bot.send_message(chat_id, "Toxic messages will not be deleted", reply_markup=gen_base_menu())
    elif call.data == "val_yes":
        chat_settings.validate_flag = True
        bot.send_message(chat_id, "Validation option will be active", reply_markup=gen_base_menu())
    elif call.data == "val_no":
        chat_settings.validate_flag = False
        bot.send_message(chat_id, "Validation option will be inactive", reply_markup=gen_base_menu())


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    settings = ChatSettings()
    settings_by_chat_id[message.chat.id] = settings_by_chat_id.get(message.chat.id, settings)
    bot.reply_to(message, "Bot started", reply_markup=gen_base_menu())


@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    chat_id = message.chat.id
    chat_settings = settings_by_chat_id[chat_id]
    if message.text == 'Settings':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        btn1 = types.KeyboardButton('Delete toxic messages?')
        btn2 = types.KeyboardButton('Validate messages?')
        markup.add(btn1).add(btn2)
        bot.send_message(message.from_user.id, 'Choose button', reply_markup=markup)
    elif message.text == 'Delete toxic messages?':
        bot.delete_message(chat_id, message.message_id)
        bot.send_message(chat_id, "Delete toxic messages?", reply_markup=gen_yes_no_markup('del_yes', 'del_no'))
    elif message.text == 'Validate messages?':
        bot.delete_message(chat_id, message.message_id)
        bot.send_message(chat_id, "Validate messages?", reply_markup=gen_yes_no_markup('val_yes', 'val_no'))
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


bot.infinity_polling()
