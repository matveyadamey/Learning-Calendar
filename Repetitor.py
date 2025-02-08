from NoteManager import NoteManager as note_manager
from NotesTableManager import NotesTableManager as ntm


class Repetitor:
    def __init__(self, user_id):
        self.user_id = str(user_id)
        self.note_man = note_manager(self.user_id)
        self.jntm = ntm(self.user_id)

    def get_reps_count(self, note_name):
        print("Возвращаю количество повторений...")
        return self.note_man.get_note_property(note_name, "reps")


    def increaseRepsCount(self, note_name):
        print("Увеличиваю количество повторений...")
        self.note_man.edit_note_property(note_name=note_name, property_name="reps", new_value=self.get_reps_count(note_name) + 1)


    def handle_repeat_note(self, note_name):
        note_content = self.note_man.read_note(note_name)

        image_paths, note_content = \
            self.note_man.get_images_from_note(note_content)

        self.increaseRepsCount(note_name)

        print("Формирую сообщение...")

        if len(image_paths) > 0:
            media_group = \
                self.note_man.get_note_with_images(image_paths, note_content)
            return media_group

        else:
            return note_content

    def handle_get_reps_count(self, message_text):
        if len(message_text.split(' ')) > 1:
            note_name = " ".join(message_text.split(' ')[1:])

            reps_count = self.get_reps_count(note_name)
            reps_msg = f"You have repeated {note_name} for {reps_count} times"
            return reps_msg
        else:
            return "Введите название заметки после команды /get_reps"
