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
            
            
            # Разбиваем содержимое на части, если оно слишком длинное
            if len(note_content) > 500:
                parts = []
                for i in range(0, len(note_content), 500):
                    part = note_content[i:i + 500]
                    if i + 500 < len(note_content):
                        last_newline = part.rfind('\n')
                        if last_newline != -1:
                            part = part[:last_newline]
                            i = i + last_newline
                    parts.append(part)
                return parts
            return note_content

        except Exception as e:
            logging.error(f"Error in handle_repeat_note: {e}")
            raise

    def handle_get_reps_count(self, note_name):
        try:
            if self.notes_df.empty or 'reps' not in self.notes_df.columns:
                return "Нет данных о повторениях или архив не загружен"
            
            # Добавляем .md к имени файла для поиска в таблице
            note_with_ext = f"{note_name}.md"
            
            # Проверяем, есть ли заметка в таблице
            if note_with_ext not in self.notes_df['note'].values:
                return f"Заметка '{note_name}' не найдена"
            
            # Получаем количество повторений для конкретной заметки
            note_reps = self.notes_df[self.notes_df['note'] == note_with_ext]['reps'].iloc[0]
            return f"Количество повторений заметки '{note_name}': {note_reps}"
        except Exception as e:
            logging.error(f"Error in handle_get_reps_count: {e}")
            raise
