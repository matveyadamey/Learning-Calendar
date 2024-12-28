import datetime
import pandas as pd
from NotesTableManager import NotesTableManager as ntm

class IntervalChecker:

    def __init__(self):
        tableManager=ntm()
        self.notes_df=tableManager.get_notes_table()

    def get_time_diff(self): 
        today = datetime.datetime.now()
        self.notes_df["time_diff"] = today - pd.to_datetime(self.notes_df.creation_date)
        return self.notes_df

    def get_notes_for_repeat(self):
        days_for_repeats=[1,3,10,30,60,180,365]
        notes_df= self.get_time_diff()
        notes_df["should_repeat"]=notes_df.time_diff.apply(lambda x: x.days in days_for_repeats)

        return notes_df[(notes_df.reps==0) | (notes_df.should_repeat)].note.apply(lambda x: str(x)[:-3]).values
        
