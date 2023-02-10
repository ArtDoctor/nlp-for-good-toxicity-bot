from utils.googlesheets_handler import append_new_cell


def handle_button_callbacks(call, bot):
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
