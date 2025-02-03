import telebot
from ConfigManager import ConfigManager as cm
from IntervalChecker import IntervalChecker as ic
from NotesTableManager import NotesTableManager as ntm

jcm = cm()
jntm = ntm()
jic = ic()

default_notes_count = jcm.get_json_value("default_notes_count")
TOKEN = jcm.get_json_value("tgbot_token")
bot = telebot.TeleBot(TOKEN)
jntm.update_notes_table()


start_message = "Привет! Я ваш помощник в учебе, буду подсказывать \
                когда и что надо повторить для лучшего усвоения материала"
error_message = "Извиняюсь, я не очень понял, что вы хотите. \
                Попробуйте еще раз с немного другой командой"


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, start_message)


@bot.message_handler(commands=['get_notes_for_repeat'])
def send_notes_for_repeat(message):
    notes = jic.get_notes_for_repeat()

    if len(message.text.split(' ')) > 1:
        user_notes_count = int(message.text.split(' ')[1])

        if user_notes_count > len(notes) - 1:
            user_notes_count = len(notes) - 1

        bot.send_message(message.chat.id,
                         text="\n".join(notes[:user_notes_count]))

    else:
        bot.send_message(message.chat.id,
                         text="\n".join(notes[:default_notes_count]))


@bot.message_handler(commands=["lets_repeat"])
def repeat_note(message):
    note_name = " ".join(message.text.split(' ')[1:])
    note_content = jntm.read_note(note_name)

    if note_content:
        bot.send_message(message.chat.id, note_content)
        jntm.increaseRepsCount(note_name)
        bot.send_message(message.chat.id, '+1 rep')
    else:
        bot.send_message(message.chat.id, error_message)


@bot.message_handler(commands=['get_reps'])
def getRepsCount(message):
    if len(message.text.split(' ')) > 1:
        note_name = " ".join(message.text.split(' ')[1:])
        note = jntm.get_note(note_name)

        if note is not None and not note.empty:
            reps_count = jntm.get_reps_count(note_name)
            print(reps_count)
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
