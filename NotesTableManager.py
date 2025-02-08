import os
import pandas as pd
from Monitor import Monitor
from ConfigManager import ConfigManager as cm
from UserArchiveManager import UserArchiveManager
import logging


class NotesTableManager:
    notes_tables = {}  # Словарь для хранения таблиц разных пользователей
    
    def __init__(self, user_id):
        self.user_id = str(user_id)
        self.user_archive_manager = UserArchiveManager()
        self.notes_table_path = f"notes_table_{self.user_id}.csv"
        
        # Создаем пустую таблицу при инициализации, если её нет
        if not os.path.exists(self.notes_table_path):
            self.create_empty_table()
    
    def save_notes_table(self):
        """Сохраняет таблицу заметок в CSV-файл для конкретного пользователя."""
        if self.user_id in NotesTableManager.notes_tables:
            NotesTableManager.notes_tables[self.user_id].to_csv(self.notes_table_path, index=True)
    
    @property
    def notes_table(self):
        """Получает таблицу заметок для конкретного пользователя."""
        return NotesTableManager.notes_tables.get(self.user_id, pd.DataFrame())
    
    @notes_table.setter
    def notes_table(self, value):
        """Устанавливает таблицу заметок для конкретного пользователя."""
        NotesTableManager.notes_tables[self.user_id] = value

    def create_empty_table(self):
        """Создает пустую таблицу с нужными колонками"""
        empty_df = pd.DataFrame(columns=['note', 'creation_date', 'reps'])
        empty_df.to_csv(self.notes_table_path, index=False)
        logging.info(f"Created empty notes table for user {self.user_id}")

    def create_notes_table(self):
        """Создает новую таблицу заметок"""
        try:
            # Проверяем, есть ли архив у пользователя
            archive_path = self.user_archive_manager.get_user_archive_path(self.user_id)
            if archive_path:
                self.monitor = Monitor(self.user_id)
                files_info = self.monitor.scan_directory()
                
                # Создаем DataFrame с нужными колонками
                data = {
                    'note': [str(path) for path in files_info.keys()],
                    'creation_date': list(files_info.values()),
                    'reps': [0] * len(files_info)
                }
                notes_df = pd.DataFrame(data)
            else:
                # Если архива нет, создаем пустую таблицу
                notes_df = pd.DataFrame(columns=['note', 'creation_date', 'reps'])
            
            # Сохраняем таблицу
            notes_df.to_csv(self.notes_table_path, index=False)
            logging.info(f"Created notes table for user {self.user_id}")
            
        except Exception as e:
            logging.error(f"Error creating notes table: {e}")
            raise

    def create_or_load_notes_table(self):
        """
        Создаёт или загружает таблицу заметок.

        Если файл таблицы существует, загружает его.
        В противном случае создаёт новую таблицу.

        :return: DataFrame с данными заметок
        """
        if os.path.exists(self.notes_table_path):
            return pd.read_csv(self.notes_table_path, index_col=0)
        else:
            print("Создаю таблицу...")
            return self.create_notes_table()

    def update_notes_table(self):
        """Обновляет существующую таблицу заметок"""
        try:
            # Получаем текущую таблицу если она есть
            if os.path.exists(self.notes_table_path):
                current_df = pd.read_csv(self.notes_table_path)
                current_reps = dict(zip(current_df['note'], current_df['reps']))
            else:
                current_reps = {}

            # Получаем новый список файлов
            files_info = self.monitor.scan_directory()
            
            # Преобразуем пути в строки
            data = {
                'note': [str(path) for path in files_info.keys()],
                'creation_date': list(files_info.values()),
                'reps': [current_reps.get(str(note), 0) for note in files_info.keys()]
            }
            new_df = pd.DataFrame(data)
            
            # Сохраняем обновленную таблицу
            new_df.to_csv(self.notes_table_path, index=False)
            logging.info(f"Updated notes table for user {self.user_id}")
            
        except Exception as e:
            logging.error(f"Error updating notes table: {e}")
            raise

    def get_notes_table(self):
        """Возвращает таблицу заметок"""
        if not os.path.exists(self.notes_table_path):
            self.create_notes_table()
        return pd.read_csv(self.notes_table_path)
