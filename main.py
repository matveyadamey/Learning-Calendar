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

def split_and_send_message(chat_id, text, max_length=4096):
    """
    Разделяет длинное сообщение на части и отправляет их последовательно
    
    :param chat_id: ID чата для отправки
    :param text: Текст для отправки
    :param max_length: Максимальная длина одного сообщения (для Telegram это 4096 символов)
    """
    # Если текст короче максимальной длины, отправляем как есть
    if len(text) <= max_length:
        bot.send_message(chat_id, text)
        return

    # Разделяем текст на части
    parts = []
    for i in range(0, len(text), max_length):
        # Находим последний перенос строки в пределах максимальной длины
        part = text[i:i + max_length]
        if i + max_length < len(text):
            # Ищем последний перенос строки
            last_newline = part.rfind('\n')
            if last_newline != -1:
                # Если нашли перенос строки, обрезаем по нему
                part = part[:last_newline]
                i = i + last_newline  # Корректируем позицию для следующей части
        parts.append(part)

    # Отправляем каждую часть
    for index, part in enumerate(parts):
        message_text = f"Часть {index + 1}/{len(parts)}\n\n{part}" if len(parts) > 1 else part
        bot.send_message(chat_id, message_text)

# Обработчик нажатий на кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = str(call.from_user.id)
    if call.data == "lets_repeat":
        bot.send_message(call.message.chat.id, "Введите название заметки для повторения:")
        bot.register_next_step_handler(call.message, handle_lets_repeat)
    elif call.data == "ask_me":
        bot.send_message(call.message.chat.id, "Введите название заметки для генерации вопросов:")
        bot.register_next_step_handler(call.message, handle_ask_me)
    elif call.data == "get_reps":
        bot.send_message(call.message.chat.id, "Введите название заметки для подсчета повторений:")
        bot.register_next_step_handler(call.message, handle_get_reps_count)
    elif call.data == "get_notes_for_repeat":
        interval_checker = ic(user_id)
        notes = interval_checker.handle_get_notes_for_repeat()
        split_and_send_message(call.message.chat.id, notes)
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
    try:
        global CHAT_ID
        user_id = str(message.from_user.id)
        CHAT_ID = message.chat.id
        
        # Создаем локальные экземпляры
        notes_table_manager = ntm(user_id)
        
        # Создаем необходимые директории и файлы для нового пользователя
        user_dir = Path("archives") / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        
        # Создаем таблицу заметок для пользователя
        notes_table_manager.create_notes_table()
        
        # Отправляем приветственное сообщение
        bot.reply_to(message, Messages.start_message, reply_markup=create_main_menu())
        
        logging.info(f"New user registered: {user_id}")
        
    except Exception as e:
        logging.error(f"Error in send_welcome: {e}")
        bot.reply_to(message, f"Произошла ошибка при регистрации: {str(e)}")

# Обработчик повторения заметки
def handle_lets_repeat(message):
    try:
        bot.send_message(message.chat.id, "Looking for note...")
        user_id = message.from_user.id
        repetitor_instance = repetitor(user_id)
        note_name = message.text
        note_content = repetitor_instance.handle_repeat_note(note_name)
        
        if isinstance(note_content, list):
            # Если контент разбит на части, отправляем каждую часть отдельно
            for i, part in enumerate(note_content, 1):
                message_text = f"Часть {i}/{len(note_content)}\n\n{part}"
                bot.send_message(message.chat.id, message_text)
        else:
            bot.send_message(message.chat.id, note_content)
        
        bot.send_message(message.chat.id, '+50 звезда')
    except Exception as e:
        logging.error(f"Error repeating note: {e}")
        bot.send_message(message.chat.id, f"An error occurred: {str(e)}")

# Обновляем функцию get_reps_count
def handle_get_reps_count(message):
    try:
        user_id = str(message.from_user.id)
        note_name = message.text
        rep = repetitor(user_id)
        reps_count = rep.handle_get_reps_count(note_name)
        bot.send_message(message.chat.id, reps_count)
    except Exception as e:
        logging.error(f"Error getting reps count: {e}")
        bot.send_message(message.chat.id, f"Произошла ошибка: {str(e)}")

@bot.message_handler(content_types=['document'])
def handle_archive_upload(message):
    print("document has sent")
    try:
        print("bobr")
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
        
        # Очищаем существующую директорию extracted, если она существует
        extract_path = user_dir / "extracted"
        print("path", user_dir)
        if user_dir.exists():
            import shutil
            shutil.rmtree(user_dir)
            print("removed")
            
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

# Добавляем новый обработчик для ask_me
def handle_ask_me(message):
    try:
        user_id = str(message.from_user.id)
        note_name = message.text
        
        bot.send_message(message.chat.id, "Генерирую вопросы с помощью ИИ...")
        
        try:
            note_man = note_manager(user_id)
            note_content = note_man.read_note(note_name)
        except ValueError as e:
            bot.send_message(message.chat.id, "Пожалуйста, сначала загрузите архив с заметками")
            return
            
        gpt_instance = gpt(user_id)
        questions = gpt_instance.generate_questions(note_content)
        split_and_send_message(message.chat.id, questions)
    except Exception as e:
        logging.error(f"Error in ask_me: {e}")
        bot.send_message(message.chat.id, f"Произошла ошибка: {str(e)}")

if __name__ == "__main__":
    logging.info("Starting bot...")
    start_scheduler()
    
    try:
        bot.polling(non_stop=True)
    except Exception as e:
        logging.error(f"Bot polling error: {e}")

logging.info("Bot stopped.")