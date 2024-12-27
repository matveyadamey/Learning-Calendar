import os
import pandas as pd
from Monitor import Monitor

class NotesTableManager: 
    def __init__(self):
            self.monitor=Monitor()
            self.notes_dict = self.monitor.scan_directory()

    def get_notes_table(self):
          if os.path.exists("notes_table.csv"):
                notes_table=pd.read_csv("notes_table.csv",index_col=0)
                return notes_table
          else:
                return self.update_notes_table()
               
    def update_notes_table(self):
          notes_table=pd.DataFrame({"note":self.notes_dict.keys(),
                                    "creation_date":pd.to_datetime(pd.Series(self.notes_dict.values())),
                                    "status":["not done"]*len(self.notes_dict)})
          
          notes_table.to_csv("notes_table.csv")
          return notes_table