from NoteManager import NoteManager as note_manager
from NotesTableManager import NotesTableManager as ntm
from ConfigManager import ConfigManager as cm


class Repetitor:
    def __init__(self):
        self.note_man = note_manager()
        self.jntm = ntm()
        self.jcm = cm()
        self.error_message = self.jcm.get_json_value("error_message")

    def increaseRepsCount(self, note_name):
        note = self.note_man.get_note(note_name)
        self.notes_table = self.jntm.get_notes_table()
        print("Увеличиваю количество повторений...")
        if note is not None:
            self.notes_table.loc[self.notes_table.note ==
                                 note_name + '.md', "reps"] += 1
            self.jntm.save_notes_table(self.notes_table)
        else:
            print(f"Не могу увеличить reps для \
                  {note_name}, так как заметка не найдена.")

    def get_reps_count(self, note_name):
        note = self.note_man.get_note(note_name)
        if note is not None and not note.empty:
            print("Возвращаю количество повторений...")
            return note.reps.values[0]
        else:
            raise "Note not found"

    def handle_repeat_note(self, note_name):
        note_content = self.note_man.read_note(note_name)

        if note_content:
            image_paths, note_content = \
                self.note_man.get_images_from_note(note_content)

            self.increaseRepsCount(note_name)

            if len(image_paths) > 0:
                media_group = \
                    self.note_man.get_note_with_images(image_paths,
                                                       note_content)
                return media_group

            else:
                return note_content
        else:
            return self.error_message

    def handle_get_reps_count(self, message_text):
        if len(message_text.split(' ')) > 1:
            note_name = " ".join(message_text.split(' ')[1:])

            reps_count = self.get_reps_count(note_name)
            reps_msg = f"You have repeated {note_name} for {reps_count} times"
            return reps_msg
        else:
            return "Введите название заметки после команды /get_reps"
