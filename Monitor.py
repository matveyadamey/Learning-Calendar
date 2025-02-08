import os
import datetime
from ConfigManager import ConfigManager as cm
from UserArchiveManager import UserArchiveManager


class Monitor:
    def __init__(self, user_id):
        """
        Инициализирует класс Monitor.

        Загружает путь к директории Obsidian из конфигурационного файла.
        """
        self.user_id = str(user_id)
        self.user_archive_manager = UserArchiveManager()
        self.obsidian_path = self.user_archive_manager.get_user_archive_path(self.user_id)
        if not self.obsidian_path:
            raise ValueError("Archive path not found for user")

    def scan_directory(self):
        """
        Сканирует указанную директорию и собирает информацию о файлах .md.

        :return: Словарь, где ключи — относительные пути к файлам,
                 а значения — даты их создания.
        """
        files_info = {}

        for root, _, files in os.walk(self.obsidian_path):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path,
                                                    self.obsidian_path)
                    creation_time = os.path.getctime(file_path)
                    creation_date = \
                        datetime.datetime.fromtimestamp(creation_time)
                    files_info[relative_path] = creation_date

        return files_info
