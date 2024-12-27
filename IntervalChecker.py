import datetime
import pandas as pd

class IntervalChecker:

    def __init__(self,notes_df):
        self.notes_df=notes_df

    def get_time_diff(self):
        
        today = datetime.datetime.now()
        repetitions = []

        self.notes_df["time_diff"] = today - self.notes_df.creation_date
        return self.notes_df

    def get_notes_for_repetition(self):
        return self.get_time_diff()
        
