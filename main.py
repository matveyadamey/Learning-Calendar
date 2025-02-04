import telebot
from ConfigManager import ConfigManager as cm
from IntervalChecker import IntervalChecker as ic
from NotesTableManager import NotesTableManager as ntm
from NoteManager import NoteManager as note_manager

jcm = cm()
jntm = ntm()
jic = ic()
note_man = note_manager()

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


def send_note_with_images(chat_id, image_paths, note_content):
    media_group = []
    image_data_list = []

    for i, path in enumerate(image_paths):
        with open(path, 'rb') as image_file:
            image_data = image_file.read()
            image_data_list.append(image_data)

        if i == 0:
            photo = telebot.types.InputMediaPhoto(image_data_list[-1],
                                                  caption=note_content)
            media_group.append(photo)
        else:
            photo = telebot.types.InputMediaPhoto(image_data_list[-1])
            media_group.append(photo)

    bot.send_media_group(chat_id, media_group)


@bot.message_handler(commands=["lets_repeat"])
def repeat_note(message):
    note_name = " ".join(message.text.split(' ')[1:])
    note_content = note_man.read_note(note_name)

    if note_content:
        image_paths, note_content = note_man.get_images_from_note(note_content)

        if len(image_paths) > 0:
            send_note_with_images(message.chat.id, image_paths, note_content)

        else:
            bot.send_message(message.chat.id, note_content)

        note_man.increaseRepsCount(note_name)
        bot.send_message(message.chat.id, '+1 rep')

    else:
        bot.send_message(message.chat.id, error_message)


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
