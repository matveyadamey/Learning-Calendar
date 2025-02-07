import os
import pandas as pd
from Monitor import Monitor
from ConfigManager import ConfigManager as cm
from Messages import Messages

class NotesTableManager:
    notes_table = pd.DataFrame()

    def __init__(self):
        """
        Инициализирует класс NotesTableManager.

        Загружает путь к таблице заметок и
        сканирует директорию для получения списка заметок.
        """
        self.monitor = Monitor()
        config_manager = cm()
        self.notes_dict = self.monitor.scan_directory()
        self.notes_table_path = "notes_table.csv"
        self.obsidian_path = config_manager.get_json_value("obsidian_path")
        self.image_folder = config_manager.get_json_value("image_folder")
    
    def save_notes_table(self):
        """
        Сохраняет таблицу заметок в CSV-файл.

        :param notes_table: DataFrame с данными заметок
        """
        NotesTableManager.notes_table.to_csv(self.notes_table_path, index=True)

    def create_notes_table(self, focus_topic = 0):
        """
        Создаёт новую таблицу заметок на основе данных из self.notes_dict.

        :return: DataFrame с данными заметок
        """
        if focus_topic == 0:
            notes = list(self.notes_dict.keys())
            creation_dates = pd.to_datetime(list(self.notes_dict.values()),
                                            format='%Y-%m-%d %H:%M:%S.%f')
            reps_counts = [0] * len(notes)

            notes_table = pd.DataFrame({
                "note": notes,
                "creation_date": creation_dates,
                "reps": reps_counts
            })
            NotesTableManager.notes_table = notes_table
            self.save_notes_table()
            return notes_table
        else:
            notes = list(self.notes_dict.keys())
            creation_dates = pd.to_datetime(list(self.notes_dict.values()),
                                            format='%Y-%m-%d %H:%M:%S.%f')
            reps_counts = [0] * len(notes)

            notes_table = pd.DataFrame({
                "note": notes,
                "creation_date": creation_dates,
                "reps": reps_counts
            })

            notes_table = notes_table[notes_table.note.apply(lambda x: focus_topic in x)]



            NotesTableManager.notes_table = notes_table
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

        NotesTableManager.notes_table = updated_table

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
    
    def handle_enter_focus_mode(self, message_text):
        topic_name = " ".join(message_text.split(' ')[1:])
        self.create_notes_table(topic_name)
        return topic_name
    
    def handle_exit_focus_mode(self):
        self.notes_dict = self.monitor.scan_directory()
        self.create_notes_table()
