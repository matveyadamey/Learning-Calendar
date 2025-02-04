import datetime
import pandas as pd
from NotesTableManager import NotesTableManager as ntm
from ConfigManager import ConfigManager as cm


class IntervalChecker:

    def __init__(self):
        tableManager = ntm()
        jcm = cm()
        self.notes_df = tableManager.get_notes_table()
        self.default_notes_count = jcm.get_json_value("default_notes_count")

    def get_time_diff(self):
        today = datetime.datetime.now()
        creation_date = pd.to_datetime(self.notes_df.creation_date)
        self.notes_df["time_diff"] = today - creation_date
        return self.notes_df

    def get_notes_for_repeat(self, message_text):
        days_for_repeats = [1, 3, 10, 30, 60, 180, 365]
        notes_df = self.get_time_diff()
        notes_df["should_repeat"] = \
            notes_df.time_diff.apply(lambda x: x.days in days_for_repeats)

        notes_for_repeat = \
            notes_df[(notes_df.reps == 0) | (notes_df.should_repeat)].note

        notes_for_repeat = notes_for_repeat.apply(lambda x: str(x)[:-3]).values

        if len(message_text.split(' ')) > 1:
            user_notes_count = int(message_text.split(' ')[1])

            if user_notes_count > len(notes_for_repeat) - 1:
                user_notes_count = len(notes_for_repeat) - 1

            return "\n".join(notes_for_repeat[:user_notes_count])

        else:
            return "\n".join(notes_for_repeat[:self.default_notes_count])
