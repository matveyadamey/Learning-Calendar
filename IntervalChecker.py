import datetime
import pandas as pd
from NotesTableManager import NotesTableManager as ntm
from ConfigManager import ConfigManager as cm
from Messages import Messages
from UserArchiveManager import UserArchiveManager
from pathlib import Path
import logging


class IntervalChecker:
    def __init__(self, user_id):
        self.user_id = str(user_id)
        self.table_manager = ntm(self.user_id)
        self.config_manager = cm(self.user_id)
        self.user_archive_manager = UserArchiveManager()
        self.notes_df = self.table_manager.get_notes_table()
        self.default_notes_count = \
            self.config_manager.get_json_value("default_notes_count")

    def calculate_time_diff(self):
        today = datetime.datetime.now()
        creation_date = pd.to_datetime(self.notes_df.creation_date)
        self.notes_df["time_diff"] = (today - creation_date).dt.days
        return self.notes_df

    def filter_notes_for_repetition(self):
        days_for_repeats = Messages.days_for_repeats
        notes_df = self.calculate_time_diff()

        # Получаем путь к архиву пользователя
        archive_path = self.user_archive_manager.get_user_archive_path(self.user_id)
        logging.info(f"Archive path for user {self.user_id}: {archive_path}")
        
        if not archive_path:
            logging.warning(f"No archive path found for user {self.user_id}")
            return []

        # Фильтруем заметки, которые есть в архиве пользователя
        notes_df = notes_df[notes_df.note.apply(lambda x: Path(archive_path) / x).apply(lambda x: x.exists())]
        logging.info(f"Found {len(notes_df)} notes in archive")

        notes_df["should_repeat"] = notes_df.time_diff.isin(days_for_repeats)
        notes_for_repetition = notes_df[
            (notes_df.reps == 0) | (notes_df.should_repeat)
        ].note.apply(lambda x: x.replace(".md", "")).tolist()
        
        logging.info(f"Notes for repetition: {notes_for_repetition}")
        return notes_for_repetition

    def handle_get_notes_for_repeat(self):
        notes_for_repetition = self.filter_notes_for_repetition()
        if not notes_for_repetition:
            return "Нет заметок для повторения или архив не загружен"
        return "\n".join(notes_for_repetition[:self.default_notes_count])
