import os
import datetime
from ConfigManager import ConfigManager as cm


class Monitor:

    def __init__(self):
        jcm = cm()
        self.obsidian_path = jcm.get_json_value("obsidian_path")

    def scan_directory(self):
        # Словарь для хранения путей и дат создания
        self.files_dict = {}

        for root, dirs, files in os.walk(self.obsidian_path):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)

                    cleaned_file_path = \
                        file_path.replace(self.obsidian_path, '')

                    self.creation_time = os.path.getctime(file_path)

                    self.files_dict[cleaned_file_path] = \
                        datetime.datetime.fromtimestamp(self.creation_time)
        return self.files_dict
