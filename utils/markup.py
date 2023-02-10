from telebot import types


def gen_del_markup():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(types.InlineKeyboardButton("Yes", callback_data="cb_yes"),
                               types.InlineKeyboardButton("No", callback_data="cb_no"))
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
