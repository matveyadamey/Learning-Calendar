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
        self.error_message = self.jcm.get_json_value("error_message")

    def read_note(self, note_path):
        path = self.obsidian_path + '/' + note_path + '.md'

        if os.path.exists(path):
            with open(path, 'r', encoding='UTF-8') as note:
                note_content = note.read()
                return note_content
        else:
            return False

    def get_note(self, note_name):
        self.notes_table = self.jntm.get_notes_table()
        cleaned_note_name = (note_name + '.md').replace("\\\\", "\\")

        note = self.notes_table[self.notes_table.note == cleaned_note_name]

        if not note.empty:
            return note
        else:
            print(f"Заметка {cleaned_note_name} не найдена.")
            return None

    def increaseRepsCount(self, note_name):
        note = self.get_note(note_name)
        self.notes_table = self.jntm.get_notes_table()
        if note is not None:
            self.notes_table[self.notes_table.note ==
                            note_name + '.md'].reps += 1
            self.jntm.save_notes_table(self.notes_table)
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

    def get_image_pathes_by_name(self, image_names):
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
        image_links = []
        file_extensions = (".png]]",".jpg]]")
        image_counter = 0
        splitted_note_content = re.split(r'(\s+)', note_content)
        
        for i, word in enumerate(splitted_note_content):
            if "![[" in word:
                note_content = note_content.replace(word, "").\
                    replace(splitted_note_content[i + 2], "")

            if word.endswith(file_extensions):
                note_content = note_content.replace(word, f"** photo {image_counter} **")
                image_links.append(word.replace("]]", ""))
                image_counter += 1 

        return self.get_image_pathes_by_name(image_links), note_content
    
    def send_note_with_images(self, image_paths, note_content):
        media_group = []
        image_data_list = []

        for i, path in enumerate(image_paths):
            with open(path, 'rb') as image_file:
                image_data = image_file.read()
                image_data_list.append(image_data)

            if i == 0:
                photo = telebot.types.InputMediaPhoto(image_data_list[-1],
                                                    caption=note_content)
                media_group.append(photo)
            else:
                photo = telebot.types.InputMediaPhoto(image_data_list[-1])
                media_group.append(photo)

        return media_group

    def repeat_note(self, note_name):
        note_content = self.read_note(note_name)

        if note_content:
            image_paths, note_content = self.get_images_from_note(note_content)

            if len(image_paths) > 0:
                media_group = self.send_note_with_images(image_paths, note_content)
                return media_group

            else:
                self.increaseRepsCount(note_name)
                return note_content
        else:
            return self.error_message
