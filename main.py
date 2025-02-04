import telebot
from ConfigManager import ConfigManager as cm
from IntervalChecker import IntervalChecker as ic
from NotesTableManager import NotesTableManager as ntm
from NoteManager import NoteManager as note_manager
from Repetitor import Repetitor as repetitor
from Messages import Messages
import pandas as pd

jcm = cm()
jntm = ntm()
jic = ic()
note_man = note_manager()
rep = repetitor()

token = jcm.get_json_value("tgbot_token")

bot = telebot.TeleBot(token)
jntm.update_notes_table()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, Messages.start_message)


@bot.message_handler(commands=['get_notes_for_repeat'])
def send_notes_for_repeat(message):
    try:
        notes = jic.handle_get_notes_for_repeat(message.text)
        bot.send_message(message.chat.id, notes)
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {str(e)}")


@bot.message_handler(commands=["lets_repeat"])
def repeat_note(message):
    try:
        bot.send_message(message.chat.id, "Looking for note...")

        note_name = " ".join(message.text.split(' ')[1:])
        note_content = rep.handle_repeat_note(note_name)

        if type(note_content) is list:
            bot.send_media_group(message.chat.id, note_content)
        else:
            bot.send_message(message.chat.id, note_content)

        bot.send_message(message.chat.id, '+1 rep')

    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {str(e)}")


@bot.message_handler(commands=['get_reps'])
def getRepsCount(message):
    try:
        bot.send_message(message.chat.id,
                         rep.handle_get_reps_count(message.text))
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {str(e)}")


print('starting bot...')

bot.polling()

print("bot stoped")
