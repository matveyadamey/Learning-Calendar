from NoteManager import NoteManager as note_manager
from NotesTableManager import NotesTableManager as ntm
import logging


class Repetitor:
    def __init__(self, user_id):
        self.user_id = str(user_id)
        self.jntm = ntm(self.user_id)
        self.jnm = note_manager(self.user_id)
        self.notes_df = self.jntm.get_notes_table()

    def get_reps_count(self, note_name):
        print("Возвращаю количество повторений...")
        return self.jnm.get_note_property(note_name, "reps")


    def increaseRepsCount(self, note_name):
        print("Увеличиваю количество повторений...")
        self.jnm.edit_note_property(note_name=note_name, property_name="reps", new_value=self.get_reps_count(note_name) + 1)


    def handle_repeat_note(self, note_name):
        try:
            # Проверяем существование таблицы и создаем ее при необходимости
            if self.notes_df.empty or 'note' not in self.notes_df.columns:
                self.jntm.create_notes_table()
                self.notes_df = self.jntm.get_notes_table()

            # Добавляем .md к имени файла для поиска в таблице
            note_with_ext = f"{note_name}.md"
            
            # Проверяем, есть ли заметка в таблице
            if note_with_ext not in self.notes_df['note'].values:
                return f"Заметка '{note_name}' не найдена"

            # Увеличиваем счетчик повторений
            mask = self.notes_df['note'] == note_with_ext
            self.notes_df.loc[mask, 'reps'] += 1
            self.notes_df.to_csv(self.jntm.notes_table_path, index=False)

            # Читаем содержимое заметки
            note_content = self.jnm.read_note(note_name)
            return note_content

        except Exception as e:
            logging.error(f"Error in handle_repeat_note: {e}")
            raise

    def handle_get_reps_count(self, message_text):
        if len(message_text.split(' ')) > 1:
            note_name = " ".join(message_text.split(' ')[1:])

            reps_count = self.get_reps_count(note_name)
            reps_msg = f"You have repeated {note_name} for {reps_count} times"
            return reps_msg
        else:
            return "Введите название заметки после команды /get_reps"
