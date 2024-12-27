import os
import json
import pandas as pd

class Monitor:

    def get_obsidian_path(self):
        json_file_path = "config.json"
        obsidian_path = ''
        with open(json_file_path, 'r') as j:
            obsidian_path = json.loads(j.read())["obsidian_path"]
        return obsidian_path

    def scan_directory(self):
        # Словарь для хранения путей и дат создания
        self.files_dict = {}

        # Проход по всем подкаталогам и файлам
        for root, dirs, files in os.walk(self.get_obsidian_path()):
            for file in files:
                if file.endswith('.md'):
                    self.creation_time = os.path.getctime(os.path.join(root, file))
                    self.files_dict[file] = self.creation_time

        return self.files_dict

    def update_notes_table(self):
        notes_dict = self.scan_directory()

        if os.path.exists("notes_table.csv"):
            notes_table=pd.read_csv("notes_table.csv",index_col=0)


        else:
            task_table=pd.DataFrame({"note":notes_dict.keys(),"creation_date":notes_dict.values(),"status":["not done"]*len(notes_dict)})
            task_table.to_csv("notes_table.csv")
mon=Monitor()
mon.update_notes_table()