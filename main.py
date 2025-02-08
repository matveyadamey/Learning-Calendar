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
    btn6 = types.InlineKeyboardButton("Загрузить архив", callback_data="upload_archive")
    markup.add(btn0, btn1, btn2, btn3, btn6)
    return markup

# Обработчик нажатий на кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = str(call.from_user.id)  # ID пользователя, который нажал кнопку
    if call.data == "lets_repeat":
        bot.send_message(call.message.chat.id, "Введите название заметки для повторения:")
        bot.register_next_step_handler(call.message, handle_lets_repeat)
    elif call.data == "ask_me":
        try:
            if Messages.last_repeated_note_name == "":
                bot.send_message(call.message.chat.id, "Эта функция доступна, если вы сегодня уже повторяли материал")
                return

            bot.send_message(call.message.chat.id, "Генерирую вопросы с помощью ИИ...")
            
            try:
                note_man = note_manager(user_id)  # Используем ID из callback
                note_content = note_man.read_note(Messages.last_repeated_note_name)
            except ValueError as e:
                bot.send_message(call.message.chat.id, "Пожалуйста, сначала загрузите архив с заметками")
                return
                
            gpt_instance = gpt(user_id)  # Используем тот же ID
            questions = gpt_instance.generate_questions(note_content)
            bot.send_message(call.message.chat.id, questions)
        except Exception as e:
            logging.error(f"Error in ask_me: {e}")
            bot.send_message(call.message.chat.id, f"Произошла ошибка: {str(e)}")
    elif call.data == "get_reps":
        get_reps_count(call.message)
    elif call.data == "get_notes_for_repeat":
        interval_checker = ic(user_id)
        notes = interval_checker.handle_get_notes_for_repeat()
        bot.send_message(call.message.chat.id, notes)
    elif call.data == "upload_archive":
        bot.send_message(call.message.chat.id, "Пожалуйста, отправьте ZIP архив заметок")
        bot.register_next_step_handler(call.message, handle_archive_upload)

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
        user_id = message.from_user.id
        repetitor_instance = repetitor(user_id)
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

# Обработчик получения количества повторений
@bot.message_handler(func=lambda message: True, commands=['get_reps'])
def get_reps_count(message):
    try:
        user_id = message.from_user.id
        rep = repetitor(user_id)
        reps_count = rep.handle_get_reps_count(message.text)
        bot.send_message(message.chat.id, reps_count)
    except Exception as e:
        logging.error(f"Error getting reps count: {e}")
        bot.send_message(message.chat.id, f"An error occurred: {str(e)}")

@bot.message_handler(content_types=['document'])
def handle_archive_upload(message):
    try:
        if not message.document:
            bot.reply_to(message, "Пожалуйста, отправьте ZIP архив")
            return
            
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

        print("archive", user_id)
        # После успешной распаковки архива:
        notes_table_manager = ntm(user_id)
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