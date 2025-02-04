import os
from ConfigManager import ConfigManager as cm
from NotesTableManager import NotesTableManager as ntm
import re
import telebot


class NoteManager:
    def __init__(self):
        self.jcm = cm()
        self.obsidian_path = self.jcm.get_json_value("obsidian_path")
        self.image_folder = self.jcm.get_json_value("image_folder")
        self.jntm = ntm()

    def read_note(self, note_path):
        path = os.path.join(self.obsidian_path, note_path + '.md')

        if os.path.exists(path):
            with open(path, 'r', encoding='UTF-8') as note:
                note_content = note.read()
                return note_content
        else:
            raise ValueError("Note not found")

    def get_note_property(self, note_name, property_name):
        notes_table = self.jntm.notes_table

        cleaned_note_name = (note_name + '.md').replace("\\\\", "\\")

        note = notes_table[notes_table.note == cleaned_note_name]

        if not note.empty:
            return note.loc[:,property_name].values[0]

        else:
            raise ValueError("Note not found")

    def edit_note_property(self, note_name, property_name, new_value):
        notes_table = self.jntm.notes_table
        cleaned_note_name = (note_name + '.md').replace("\\\\", "\\")

        note = notes_table[notes_table.note == cleaned_note_name]

        if not note.empty:
            notes_table.loc[notes_table.note == cleaned_note_name, property_name] = new_value

        else:
            raise ValueError("Note not found")
        
        self.jntm.save_notes_table()


    def get_correct_image_paths(self, image_names):
        """
        форматирует и проверяет на корректность пути к изображениям
        return: list путей типа string
        """
        image_pathes = []

        for name in image_names:
            path = self.image_folder + "/" + name

            if os.path.exists(path):
                image_pathes.append(path)
            else:
                edited_path = self.image_folder + "/" + "Pasted image " + name

                if os.path.exists(edited_path):
                    image_pathes.append(edited_path)
                else:
                    print("sorry не нашел картинку")

        return image_pathes

    def get_images_from_note(self, note_content):
        """
        извлекает названия изображений из заметки
        заменяет их в тексте
        return: (list путей к изображениям, исправленный текст заметки)
        """
        image_links = []
        file_extensions = (".png]]", ".jpg]]")
        image_counter = 0
        splitted_note_content = re.split(r'(\s+)', note_content)
        

        for i, word in enumerate(splitted_note_content):
            if "![[" in word:
                note_content = note_content.replace(word, "").\
                    replace(splitted_note_content[i + 2], "")

            if word.endswith(file_extensions):
                note_content = note_content.replace(word, f"** photo {image_counter} **")
                photo_name_replacer = f"** photo {image_counter} **"
                note_content = note_content.replace(word,
                                                    photo_name_replacer)
                image_links.append(word.replace("]]", ""))
                image_counter += 1

        return self.get_correct_image_paths(image_links), note_content
    
    def get_note_with_images(self, image_paths, note_content):
            """
            генерирует сообщение с картинками
            """
            media_group = [
                telebot.types.InputMediaPhoto(open(path, 'rb').read(),
                                            caption=note_content
                                            if i == 0 else None)
                for i, path in enumerate(image_paths)
            ]
            return media_group
