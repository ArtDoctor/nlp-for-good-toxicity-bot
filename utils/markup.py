from telebot import types


def gen_yes_no_markup(yes_text, no_text):
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(types.InlineKeyboardButton("✅ Yes", callback_data=yes_text),
                               types.InlineKeyboardButton("❌ No", callback_data=no_text))
    return markup


def gen_base_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Settings")
    markup.add(btn1)
    return markup


def validation_markup():
    val_markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton('😡 Toxic', callback_data='toxic')
    button2 = types.InlineKeyboardButton('👌 Not toxic', callback_data='non_toxic')
    val_markup.add(button, button2)
    return val_markup
