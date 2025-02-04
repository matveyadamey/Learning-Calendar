import telebot
from ConfigManager import ConfigManager as cm
from IntervalChecker import IntervalChecker as ic
from NotesTableManager import NotesTableManager as ntm
from NoteManager import NoteManager as note_manager

jcm = cm()
jntm = ntm()
jic = ic()
note_man = note_manager()

start_message = jcm.get_json_value("start_message")
error_message = jcm.get_json_value("error_message")
token = jcm.get_json_value("tgbot_token")

bot = telebot.TeleBot(token)
jntm.update_notes_table()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, start_message)


@bot.message_handler(commands=['get_notes_for_repeat'])
def send_notes_for_repeat(message):
    notes = jic.get_notes_for_repeat(message.text)
    bot.send_message(message.chat.id, notes)


@bot.message_handler(commands=["lets_repeat"])
def repeat_note(message):
    note_name = " ".join(message.text.split(' ')[1:])
    note_content = note_man.repeat_note(note_name)
    
    if type(note_content) == list:
        bot.send_media_group(message.chat.id, note_content)
    else: 
        bot.send_message(message.chat.id, note_content)

    bot.send_message(message.chat.id, '+1 rep')


@bot.message_handler(commands=['get_reps'])
def getRepsCount(message):
    if len(message.text.split(' ')) > 1:
        note_name = " ".join(message.text.split(' ')[1:])
        note = note_man.get_note(note_name)

        if note is not None and not note.empty:
            reps_count = note_man.get_reps_count(note_name)
            reps_msg = f"You have repeated {note_name} for {reps_count} times"
            bot.send_message(message.chat.id, reps_msg)
        else:
            bot.send_message(message.chat.id,
                             f"Заметка '{note_name}' не найдена.")
    else:
        bot.send_message(message.chat.id,
                         "Введите название заметки после команды /get_reps")


print('starting bot...')

bot.polling()

print("bot stoped")
