import os
import telebot
from dotenv import load_dotenv
from utils.ai import predict
from googletrans import Translator
import speech_recognition as sr
from pydub import AudioSegment

load_dotenv()
BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)
translator = Translator()
speech_recognizer = sr.Recognizer()


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


@bot.message_handler(content_types=['voice'])
def handle_voice_message(message):
    raw = message.voice.file_id
    src_path = "utils/downloaded_files/" + raw + ".ogg"
    dest_path = "utils/downloaded_files/" + raw + ".wav"
    file_info = bot.get_file(raw)
    downloaded_file = bot.download_file(file_info.file_path)
    with open(src_path, 'wb') as new_file:
        new_file.write(downloaded_file)

    AudioSegment.from_file(src_path).export(dest_path, format='wav')

    with sr.AudioFile(dest_path) as source:
        # listen for the data (load audio to memory)
        audio_data = speech_recognizer.record(source)
        # recognize (convert from speech to text)
        try:
            text, conf = speech_recognizer.recognize_google(audio_data, with_confidence=True)
        except sr.UnknownValueError:
            print("Could not understand audio")
            return
        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))
            return
        print("Confidence = {}".format(conf))
        # text = translator.translate(text).text
        if conf <= 0.7:
            return
        prob = predict(text)[0][1]
        if prob > 0.7:
            bot.reply_to(message, 'toxicity detected: ' + str(prob))
        else:
            bot.reply_to(message, prob)
        os.remove(src_path)
    os.remove(dest_path)


bot.infinity_polling()
