import os
import telebot
from dotenv import load_dotenv
from utils.ai import predict
from googletrans import Translator

load_dotenv()
os.environ['BOT_TOKEN'] = "6006159686:AAFQiVoYW9DQa5I8NvgzpYJBnx9mC8PFV48"
BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)
translator = Translator()


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Bot started")


@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    text = translator.translate(message.text).text
    prob = predict(text)[0][1]
    if prob > 0.7:
        bot.reply_to(message, 'toxicity detected: ' + str(prob))
    else:
        bot.reply_to(message, prob)


bot.infinity_polling()
