import datetime
import pandas as pd
from NotesTableManager import NotesTableManager as ntm
from ConfigManager import ConfigManager as cm
from Messages import Messages


class IntervalChecker:
    def __init__(self):
        self.table_manager = ntm()
        self.config_manager = cm()
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

        notes_df["should_repeat"] = notes_df.time_diff.isin(days_for_repeats)

        notes_for_repetition = notes_df[
            (notes_df.reps == 0) | (notes_df.should_repeat)
        ].note.apply(lambda x: x.replace(".md", "")).tolist()

        return notes_for_repetition

    def handle_get_notes_for_repeat(self, message_text):
        notes_for_repetition = self.filter_notes_for_repetition()
        
        user_notes_count = int(message_text.split(" ")[0])

        if user_notes_count > len(notes_for_repetition):
                    user_notes_count = len(notes_for_repetition)
        if user_notes_count > 100:
                    user_notes_count = self.default_notes_count

        return "\n".join(notes_for_repetition[:user_notes_count])
