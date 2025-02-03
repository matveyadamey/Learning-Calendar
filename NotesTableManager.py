import os
import pandas as pd
from Monitor import Monitor
from ConfigManager import ConfigManager as cm


class NotesTableManager:
    def __init__(self):
        self.monitor = Monitor()
        jcm = cm()
        self.notes_dict = self.monitor.scan_directory()
        self.notes_table_path = "notes_table.csv"
        self.obsidian_path = jcm.get_json_value("obsidian_path")

    def form_notes_table(self, notes, creation_dates, reps_counts):
        creation_date = pd.to_datetime(pd.Series(creation_dates),
                                       format='%Y-%m-%d %H:%M:%S.%f')
        notes_table = pd.DataFrame({"note": notes,
                                    "creation_date": creation_date,
                                    "reps": reps_counts})
        self.notes_table = notes_table
        return notes_table

    def create_notes_table(self):
        self.form_notes_table(self.notes_dict.keys(),
                              self.notes_dict.values(),
                              [0] * len(self.notes_dict))
        self.save_notes_table()
        return self.notes_table

    def save_notes_table(self):
        self.notes_table.to_csv(self.notes_table_path)

    def get_notes_table(self):
        if os.path.exists(self.notes_table_path):
            notes_table = pd.read_csv(self.notes_table_path, index_col=0)
            return notes_table
        else:
            print("Создаю таблицу...")
            return self.create_notes_table()

    def update_notes_table(self):
        notes = []
        creation_dates = []
        reps_counts = []

        notes_table = self.get_notes_table()
        for note_name in self.notes_dict.keys():
            row = notes_table[notes_table.note == note_name]

            if row.shape[0] != 0:
                notes.append(row.note.values[0])
                creation_dates.append(row.creation_date.values[0])
                reps_counts.append(row.reps.values[0])
            else:
                notes.append(note_name)
                creation_dates.append(self.notes_dict[note_name])
                reps_counts.append(0)
        self.form_notes_table(notes, creation_dates, reps_counts)
        self.save_notes_table()

    def read_note(self, note_path):
        path = self.obsidian_path + '/' + note_path + '.md'

        if os.path.exists(path):
            with open(path, 'r', encoding='UTF-8') as note:
                note_content = note.read()
                return note_content
        else:
            return False

    def get_note(self, note_name):
        self.notes_table = pd.DataFrame(self.get_notes_table())
        cleaned_note_name = (note_name + '.md').replace("\\\\", "\\")

        note = self.notes_table[self.notes_table.note == cleaned_note_name]

        if not note.empty:
            return note
        else:
            print(f"Заметка {cleaned_note_name} не найдена.")
            return None

    def increaseRepsCount(self, note_name):
        note = self.get_note(note_name)
        if note is not None:
            self.notes_table.loc[self.notes_table.note ==
                                 note_name + '.md', 'reps'] += 1
            self.save_notes_table()
        else:
            print(f"Не могу увеличить reps для \
                  {note_name}, так как заметка не найдена.")

    def get_reps_count(self, note_name):
        note = self.get_note(note_name)
        if note is not None and not note.empty:
            return note.reps.values[0]
        else:
            print(f"Заметка {note_name} не найдена.")
            return 0
