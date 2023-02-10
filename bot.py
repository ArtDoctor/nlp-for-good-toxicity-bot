import os
import telebot
from telebot import types
from dotenv import load_dotenv
from utils.ai import predict
from googletrans import Translator
from utils.button_handler import handle_button_callbacks

load_dotenv()
BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)
translator = Translator()


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Bot started")


@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    # AI and probability
    text = translator.translate(message.text).text
    prob = predict(text)[0][1]
    if prob > 0.7:
        response = 'toxicity detected: ' + str(prob)
    else:
        response = str(prob)

    # Buttons for validation
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton('😡 Токсично', callback_data='toxic')
    button2 = types.InlineKeyboardButton('👌 Не токсично', callback_data='non_toxic')
    markup.add(button, button2)

    # Send message with buttons
    bot.reply_to(message, response, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    handle_button_callbacks(call, bot)


bot.infinity_polling()

