import os
import pandas as pd
from Monitor import Monitor
from ConfigManager import ConfigManager as cm


class NotesTableManager:
    notes_tables = {}  # Словарь для хранения таблиц разных пользователей
    
    def __init__(self, user_id):
        self.user_id = str(user_id)
        self.monitor = Monitor(user_id)
        self.config_manager = cm(user_id)
        self.notes_dict = self.monitor.scan_directory()
        self.notes_table_path = f"notes_table_{self.user_id}.csv"
        self.obsidian_path = self.config_manager.get_json_value("obsidian_path")
        self.image_folder = self.config_manager.get_json_value("image_folder")
    
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

    def create_notes_table(self):
        """
        Создаёт новую таблицу заметок на основе данных из self.notes_dict.

        :return: DataFrame с данными заметок
        """
        notes = list(self.notes_dict.keys())
        creation_dates = pd.to_datetime(list(self.notes_dict.values()),
                                        format='%Y-%m-%d %H:%M:%S.%f')
        reps_counts = [0] * len(notes)

        notes_table = pd.DataFrame({
            "note": notes,
            "creation_date": creation_dates,
            "reps": reps_counts
        })
        self.notes_table = notes_table
        self.save_notes_table()
        return notes_table
    

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
        """
        Обновляет таблицу заметок,
        добавляя новые заметки и обновляя существующие.

        :return: Обновлённый DataFrame с данными заметок
        """
        existing_table = self.create_or_load_notes_table()

        new_notes = list(self.notes_dict.keys())
        new_creation_dates = pd.to_datetime(list(self.notes_dict.values()),
                                            format='%Y-%m-%d %H:%M:%S.%f')
        new_reps_counts = [0] * len(new_notes)

        new_table = pd.DataFrame({
            "note": new_notes,
            "creation_date": new_creation_dates,
            "reps": new_reps_counts
        })

        updated_table = pd.concat([existing_table, new_table]).\
            drop_duplicates(subset="note", keep="first")

        self.notes_table = updated_table

        self.save_notes_table()

        return updated_table

    def get_notes_table(self):
        """
        Получает таблицу заметок.

        Если файл таблицы существует, загружает его.
        В противном случае создаёт новую таблицу.

        :return: DataFrame с данными заметок
        """
        return self.create_or_load_notes_table()
