import os
import pandas as pd
from Monitor import Monitor
from ConfigManager import ConfigManager as cm

class NotesTableManager: 
      def __init__(self):
            self.monitor=Monitor()
            self.notes_dict = self.monitor.scan_directory()
            self.notes_table_path="notes_table.csv"
            jcm=cm()
            self.obsidian_path=jcm.get_json_value("obsidian_path")
      
      def form_notes_table(self,notes,creation_dates,reps_counts):
            notes_table=pd.DataFrame({"note":notes,
                                    "creation_date":pd.to_datetime(pd.Series(creation_dates),format='%Y-%m-%d %H:%M:%S.%f'),
                                    "reps":reps_counts})
            return notes_table
           
               
      def create_notes_table(self):
            notes_table=self.form_notes_table(self.notes_dict.keys(),
                                    self.notes_dict.values(),
                                    [0]*len(self.notes_dict))
          
            self.save_notes_table(notes_table)
            return notes_table
      
      def save_notes_table(self,notes_table):
           notes_table.to_csv(self.notes_table_path)

      def get_notes_table(self):
           if os.path.exists(self.notes_table_path):
                notes_table=pd.read_csv(self.notes_table_path,index_col=0)
                return notes_table
           else:
                return self.create_notes_table()
      
      def update_notes_table(self):
            notes=[]
            creation_dates=[]
            reps_counts=[]

            notes_table=self.get_notes_table()
            for note_name in self.notes_dict.keys():
                  row=notes_table[notes_table.note==note_name]

                  if row.shape[0]!=0:
                      notes.append(row.note.values[0])
                      creation_dates.append(row.creation_date.values[0])
                      reps_counts.append(row.reps.values[0])
                  else:
                      notes.append(note_name)
                      creation_dates.append(self.notes_dict[note_name])
                      reps_counts.append(0)   

            self.save_notes_table(self.form_notes_table(notes,creation_dates,reps_counts))      

      
      def get_note(self,note_path):
            path=self.obsidian_path+'/'+note_path+'.md'
            if os.path.exists(path):
                  with open(path,'r',encoding='UTF-8') as note:
                        return note.read()
            else:
                 return False
      
      def increaseRepsCount(self, note_name):
           notes_table=self.get_notes_table()
           note=(note_name+'.md').replace("\\\\", "\\")
           print(note)
           notes_table.loc[notes_table.note==note,"reps"]+=1
           self.save_notes_table(notes_table)
      
      def get_reps_count(self,note_name):
           notes_table=self.get_notes_table()
           note=(note_name+'.md').replace("\\\\", "\\")
           print(note)
           return notes_table[notes_table.note==note]['reps'].values[0]