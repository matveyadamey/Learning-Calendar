import telebot
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

# Обработчик установки пути к Obsidian
@bot.message_handler(commands=['set_obsidian_path'])
def set_obsidian_path(message):
    """
    Записывает в json путь к папке obsidian.
    """
    try:
        obsidian_path = message.text.split(" ", 1)[1]
        jcm.edit_field("obsidian_path", obsidian_path + "\\")
        new_path_value = jcm.get_json_value("obsidian_path")
        logging.info(f"Obsidian path updated to: {new_path_value}")
        bot.reply_to(message, f"Obsidian path updated to: {new_path_value}")
    except IndexError:
        bot.reply_to(message, "Please provide a valid path after the command.")
    except Exception as e:
        logging.error(f"Error setting obsidian path: {e}")
        bot.reply_to(message, f"An error occurred: {str(e)}")

# Обработчик установки пути к папке с изображениями
@bot.message_handler(commands=['set_image_folder'])
def set_image_folder(message):
    """
    Записывает в json путь к папке с изображениями.
    """
    try:
        image_folder = message.text.split(" ", 1)[1]
        jcm.edit_field("image_folder", image_folder)
        new_path_value = jcm.get_json_value("image_folder")
        logging.info(f"Image folder updated to: {new_path_value}")
        bot.reply_to(message, f"Image folder updated to: {new_path_value}")
    except IndexError:
        bot.reply_to(message, "Please provide a valid path after the command.")
    except Exception as e:
        logging.error(f"Error setting image folder: {e}")
        bot.reply_to(message, f"An error occurred: {str(e)}")

# Отправка запланированного сообщения
def send_scheduled_message():
    """
    Функция для отправки автоматических сообщений.
    """
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
    """
    Бесконечный цикл для выполнения задач из schedule.
    """
    while True:
        schedule.run_pending()
        time.sleep(1)

def start_scheduler():
    """
    Запуск планировщика в отдельном потоке.
    """
    thread = threading.Thread(target=run_scheduler)
    thread.daemon = True
    thread.start()

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    """
    Обработчик команды /start.
    """
    global CHAT_ID
    CHAT_ID = message.chat.id
    bot.reply_to(message, Messages.start_message)
    bot.reply_to(message, "Scheduler started!")
    schedule.every(1).minutes.do(send_scheduled_message)

# Обработчик получения заметок для повторения
@bot.message_handler(commands=['get_notes_for_repeat'])
def send_notes_for_repeat(message):
    try:
        notes = jic.handle_get_notes_for_repeat(message.text)
        bot.send_message(message.chat.id, notes)
    except Exception as e:
        logging.error(f"Error getting notes for repeat: {e}")
        bot.send_message(message.chat.id, f"An error occurred: {str(e)}")

# Обработчик повторения заметки
@bot.message_handler(commands=["lets_repeat"])
def repeat_note(message):
    try:
        bot.send_message(message.chat.id, "Looking for note...")
        note_name = " ".join(message.text.split(' ')[1:])
        note_content = rep.handle_repeat_note(note_name)
        
        if isinstance(note_content, list):
            bot.send_media_group(message.chat.id, note_content)
        else:
            bot.send_message(message.chat.id, note_content)
        
        bot.send_message(message.chat.id, '+1 rep')
        questions = yandex_gpt.generate_questions(note_man.read_note(note_name))
        bot.send_message(message.chat.id, questions)
    except Exception as e:
        logging.error(f"Error repeating note: {e}")
        bot.send_message(message.chat.id, f"An error occurred: {str(e)}")

# Обработчик получения количества повторений
@bot.message_handler(commands=['get_reps'])
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