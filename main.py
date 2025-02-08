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
import os
import zipfile
from pathlib import Path
from UserArchiveManager import UserArchiveManager

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Инициализация компонентов
jcm = cm()
user_archive_manager = UserArchiveManager()

# Получение токена из конфигурации
token = jcm.get_json_value("tgbot_token")
bot = telebot.TeleBot(token)

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
    btn6 = types.InlineKeyboardButton("Загрузить архив", callback_data="upload_archive")
    markup.add(btn0, btn1, btn2, btn3, btn4, btn5, btn6)
    return markup

# Обработчик нажатий на кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = str(call.from_user.id)
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
    elif call.data == "upload_archive":
        bot.send_message(call.message.chat.id, "Пожалуйста, отправьте ZIP архив заметок")
        bot.register_next_step_handler(call.message, handle_archive_upload)

@bot.message_handler(func=lambda message: True, commands=['get_notes_for_repeat'])
def get_notes_for_repeat(message):
    try:
        user_id = str(message.from_user.id)
        interval_checker = ic(user_id)
        notes = interval_checker.handle_get_notes_for_repeat(user_id)
        bot.send_message(message.chat.id, notes)
    except Exception as e:
        logging.error(f"Error getting notes for repeat: {e}")
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
def send_scheduled_message(user_id):
    if CHAT_ID:
        try:
            interval_checker = ic(user_id)
            notes = interval_checker.handle_get_notes_for_repeat("")
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
    user_id = str(message.from_user.id)
    CHAT_ID = message.chat.id
    
    # Создаем локальные экземпляры
    notes_table_manager = ntm(user_id)
    interval_checker = ic(user_id)
    note_manager_instance = note_manager(user_id)
    repetitor_instance = repetitor(user_id)
    gpt_instance = gpt(user_id)
    
    bot.reply_to(message, Messages.start_message, reply_markup=create_main_menu())
  
    # schedule.every(24*60).minutes.do(lambda: send_scheduled_message(user_id))
    
    notes_table_manager.update_notes_table()

# Обработчик повторения заметки
def handle_lets_repeat(message):
    try:
        bot.send_message(message.chat.id, "Looking for note...")
        repetitor_instance = repetitor(message.from_user.id)
        note_name = message.text
        note_content = repetitor_instance.handle_repeat_note(note_name)
        
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
        note_man = note_manager(message.from_user.id)
        gpt_instance = gpt(message.from_user.id)
        questions = gpt_instance.generate_questions(note_man.read_note(Messages.last_repeated_note_name))
        bot.send_message(message.chat.id, questions)
    else:
        bot.send_message(message.chat.id, "Эта функция доступна, если вы сегодня уже повторяли материал")

# Обработчик получения количества повторений
@bot.message_handler(func=lambda message: True, commands=['get_reps'])
def get_reps_count(message):
    try:
        rep = repetitor(message.from_user.username)
        reps_count = rep.handle_get_reps_count(message.text)
        bot.send_message(message.chat.id, reps_count)
    except Exception as e:
        logging.error(f"Error getting reps count: {e}")
        bot.send_message(message.chat.id, f"An error occurred: {str(e)}")

@bot.message_handler(content_types=['document'])
def handle_archive_upload(message):
    try:
        if not message.document.file_name.endswith('.zip'):
            bot.reply_to(message, "Пожалуйста, отправьте файл в формате ZIP")
            return

        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Создаем директорию для архивов пользователя
        user_id = str(message.from_user.id)
        user_dir = Path("archives") / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        
        # Очищаем существующую директорию extracted, если она существует
        extract_path = user_dir / "extracted"
        if extract_path.exists():
            import shutil
            shutil.rmtree(extract_path)
        extract_path.mkdir(parents=True, exist_ok=True)
        
        archive_path = user_dir / message.document.file_name
        
        # Сохраняем архив
        with open(archive_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        # Распаковываем архив с правильной кодировкой
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            # Создаем список файлов с декодированными именами
            for file_info in zip_ref.filelist:
                try:
                    # Пробуем разные кодировки
                    filename = file_info.filename
                    for encoding in ['cp866', 'utf-8', 'cp1251']:
                        try:
                            filename = file_info.filename.encode('cp437').decode(encoding)
                            break
                        except UnicodeError:
                            continue
                    
                    # Создаем полный путь для файла
                    target_path = extract_path / filename
                    
                    # Создаем все промежуточные директории
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Извлекаем файл с декодированным именем
                    zip_ref.extract(file_info, path=extract_path)
                    
                    # Если имя файла было в другой кодировке, переименовываем его
                    extracted_path = extract_path / file_info.filename
                    if filename != file_info.filename and extracted_path.exists():
                        extracted_path.rename(target_path)
                            
                except Exception as e:
                    logging.error(f"Error extracting file {file_info.filename}: {e}")
                    continue

        # После успешной распаковки архива:
        notes_table_manager = ntm(message.from_user.id)
        notes_table_manager.update_notes_table()  # Обновляем таблицу заметок

        # Сохраняем путь к распакованному архиву пользователя
        global user_archive_manager
        user_archive_manager.add_user_archive(user_id, str(extract_path))

        bot.reply_to(message, f"Архив успешно распакован и заметки обновлены")
        
        # Удаляем исходный архив
        archive_path.unlink()
        
    except Exception as e:
        logging.error(f"Error handling archive: {e}")
        bot.reply_to(message, f"Произошла ошибка при обработке архива: {str(e)}")

if __name__ == "__main__":
    logging.info("Starting bot...")
    start_scheduler()
    
    try:
        bot.polling(non_stop=True)
    except Exception as e:
        logging.error(f"Bot polling error: {e}")

logging.info("Bot stopped.")