import telebot
from telebot import types
from ConfigManager import ConfigManager as cm
from IntervalChecker import IntervalChecker as ic
from NotesTableManager import NotesTableManager as ntm
from NoteManager import NoteManager as note_manager
from Repetitor import Repetitor as repetitor
from Messages import Messages
from YandexQuestionGenerator import YandexQuestionGenerator as gpt
import schedule
import time
import threading
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Инициализация компонентов
jcm = cm()
jntm = ntm()
jic = ic()
note_man = note_manager()
rep = repetitor()
yandex_gpt = gpt()

# Получение токена из конфигурации
token = jcm.get_json_value("tgbot_token")
bot = telebot.TeleBot(token)

# Обновление таблицы заметок при старте
jntm.update_notes_table()

# Глобальная переменная для CHAT_ID
CHAT_ID = None

# Создание главного меню с кнопками
def create_main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn0 = types.InlineKeyboardButton("Вывести список заметок для повторения", callback_data="get_notes_for_repeat")
    btn1 = types.InlineKeyboardButton("Повторить материал", callback_data="lets_repeat")
    btn2 = types.InlineKeyboardButton("Получить вопросы", callback_data="ask_me")
    btn3 = types.InlineKeyboardButton("Посмотреть статистику повторений", callback_data="get_reps")
    btn4 = types.InlineKeyboardButton("Настроить путь к Obsidian", callback_data="set_obsidian_path")
    btn5 = types.InlineKeyboardButton("Настроить путь к изображениям", callback_data="set_image_folder")
    markup.add(btn0, btn1, btn2, btn3, btn4, btn5)
    return markup

# Обработчик нажатий на кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "lets_repeat":
        bot.send_message(call.message.chat.id, "Введите название заметки для повторения:")
        bot.register_next_step_handler(call.message, handle_lets_repeat)
    elif call.data == "ask_me":
        ask_me(call.message)
    elif call.data == "get_reps":
        get_reps_count(call.message)
    elif call.data == "set_obsidian_path":
        bot.send_message(call.message.chat.id, "Введите путь к папке Obsidian:")
        bot.register_next_step_handler(call.message, set_obsidian_path)
    elif call.data == "set_image_folder":
        bot.send_message(call.message.chat.id, "Введите путь к папке с изображениями:")
        bot.register_next_step_handler(call.message, set_image_folder)
    elif call.data == "get_notes_for_repeat":
        get_notes_for_repeat(call.message)


@bot.message_handler(func=lambda message: True, commands=['get_notes_for_repeat'])
def get_notes_for_repeat(message):
    try:
        notes = jic.handle_get_notes_for_repeat()
        bot.send_message(message.chat.id, notes)
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {str(e)}")

# Обработчик установки пути к Obsidian
def set_obsidian_path(message):
    try:
        obsidian_path = message.text
        jcm.edit_field("obsidian_path", obsidian_path + "\\")
        new_path_value = jcm.get_json_value("obsidian_path")
        logging.info(f"Obsidian path updated to: {new_path_value}")
        bot.reply_to(message, f"Obsidian path updated to: {new_path_value}")
    except Exception as e:
        logging.error(f"Error setting obsidian path: {e}")
        bot.reply_to(message, f"An error occurred: {str(e)}")

# Обработчик установки пути к папке с изображениями
def set_image_folder(message):
    try:
        image_folder = message.text
        jcm.edit_field("image_folder", image_folder)
        new_path_value = jcm.get_json_value("image_folder")
        logging.info(f"Image folder updated to: {new_path_value}")
        bot.reply_to(message, f"Image folder updated to: {new_path_value}")
    except Exception as e:
        logging.error(f"Error setting image folder: {e}")
        bot.reply_to(message, f"An error occurred: {str(e)}")

# Отправка запланированного сообщения
def send_scheduled_message():
    if CHAT_ID:
        try:
            notes = jic.handle_get_notes_for_repeat("")
            bot.send_message(CHAT_ID, notes)
            logging.info("Scheduled message sent successfully.")
        except Exception as e:
            logging.error(f"Error sending scheduled message: {e}")
            bot.send_message(CHAT_ID, f"An error occurred: {str(e)}")
    else:
        logging.warning("CHAT_ID is not set!")

# Запуск планировщика
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

def start_scheduler():
    thread = threading.Thread(target=run_scheduler)
    thread.daemon = True
    thread.start()

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    global CHAT_ID
    CHAT_ID = message.chat.id
    bot.reply_to(message, Messages.start_message, reply_markup=create_main_menu())
    schedule.every(24*60).minutes.do(send_scheduled_message)

# Обработчик повторения заметки
def handle_lets_repeat(message):
    try:
        bot.send_message(message.chat.id, "Looking for note...")
        note_name = message.text
        note_content = rep.handle_repeat_note(note_name)
        
        if isinstance(note_content, list):
            bot.send_media_group(message.chat.id, note_content)
        else:
            bot.send_message(message.chat.id, note_content)
        
        Messages.last_repeated_note_name = note_name
        bot.send_message(message.chat.id, '+1 rep')
    except Exception as e:
        logging.error(f"Error repeating note: {e}")
        bot.send_message(message.chat.id, f"An error occurred: {str(e)}")

# Обработчик генерации вопросов
@bot.message_handler(func=lambda message: True, commands=["ask_me"])
def ask_me(message):
    bot.send_message(message.chat.id, "Генерирую вопросы с помощью ИИ...")
    if Messages.last_repeated_note_name != "":
        questions = yandex_gpt.generate_questions(note_man.read_note(Messages.last_repeated_note_name))
        bot.send_message(message.chat.id, questions)
    else:
        bot.send_message(message.chat.id, "Эта функция доступна, если вы сегодня уже повторяли материал")

# Обработчик получения количества повторений
@bot.message_handler(func=lambda message: True, commands=['get_reps'])
def get_reps_count(message):
    try:
        reps_count = rep.handle_get_reps_count(message.text)
        bot.send_message(message.chat.id, reps_count)
    except Exception as e:
        logging.error(f"Error getting reps count: {e}")
        bot.send_message(message.chat.id, f"An error occurred: {str(e)}")

if __name__ == "__main__":
    logging.info("Starting bot...")
    start_scheduler()
    
    try:
        bot.polling(non_stop=True)
    except Exception as e:
        logging.error(f"Bot polling error: {e}")

logging.info("Bot stopped.")