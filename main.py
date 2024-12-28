import telebot
from ConfigManager import ConfigManager as cm
from IntervalChecker import IntervalChecker as ic
from NotesTableManager import NotesTableManager as ntm

jcm=cm()
jntm=ntm()

jntm.update_notes_table()

jic=ic()


default_notes_count=jcm.get_json_value("default_notes_count")
TOKEN = jcm.get_json_value("tgbot_token")
bot = telebot.TeleBot(TOKEN)


start_message="Привет! Я ваш помощник в учебе, буду подсказывать когда и что надо повторить для лучшего усвоения материала"
error_message= "Извиняюсь, я не очень понял, что вы хотите. Попробуйте еще раз с немного другой командой"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, start_message)

@bot.message_handler(commands=['get_notes_for_repeat'])
def send_notes_for_repeat(message):
    notes=jic.get_notes_for_repeat()
    try:
        notes_count=int(message.text.split(' ')[1])
        bot.send_message(message.chat.id, text=str(notes[:min(len(notes)-1,notes_count)]))
    except IndexError:
        bot.send_message(message.chat.id, text=str(notes[:default_notes_count]))



@bot.message_handler(commands=["lets_repeat"])
def repeat_note(message):
    note_name=message.text.split(' ')[1].replace("'","")
    note_content= jntm.get_note(note_name)
    if note_content:
        bot.send_message(message.chat.id,note_content)
        jntm.increaseRepsCount(note_name)
        bot.send_message(message.chat.id,'+1 rep')
    else:
        bot.send_message(message.chat.id,error_message)


@bot.message_handler(commands=['get_reps'])
def getRepsCount(message):
    note_name=message.text.split(' ')[1].replace("'","")
    note= jntm.get_note(note_name)
    print(note)
    if note:
        reps_msg="You have repeated "+ note_name+" for "+str(jntm.get_reps_count(note_name)) + " times"
        bot.send_message(message.chat.id,reps_msg)
    else:
        bot.send_message(message.chat.id,error_message)


print('starting bot...')

bot.polling()

print("bot stoped")


