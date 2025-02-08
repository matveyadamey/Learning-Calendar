import json
import os
from pathlib import Path

class UserArchiveManager:
    def __init__(self):
        self.archive_paths_file = "user_archives.json"
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Создает файл с путями архивов, если он не существует"""
        if not os.path.exists(self.archive_paths_file):
            with open(self.archive_paths_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=4)

    def add_user_archive(self, user_id: str, archive_path: str):
        """Добавляет или обновляет путь к архиву пользователя"""
        with open(self.archive_paths_file, 'r', encoding='utf-8') as f:
            archives = json.load(f)
        
        archives[str(user_id)] = str(archive_path)
        
        with open(self.archive_paths_file, 'w', encoding='utf-8') as f:
            json.dump(archives, f, ensure_ascii=False, indent=4)

    def get_user_archive_path(self, user_id: str) -> str:
        """Получает путь к архиву пользователя"""
        with open(self.archive_paths_file, 'r', encoding='utf-8') as f:
            archives = json.load(f)
        
        return archives.get(str(user_id))

    def remove_user_archive(self, user_id: str):
        """Удаляет информацию об архиве пользователя"""
        with open(self.archive_paths_file, 'r', encoding='utf-8') as f:
            archives = json.load(f)
        
        if str(user_id) in archives:
            del archives[str(user_id)]
            
            with open(self.archive_paths_file, 'w', encoding='utf-8') as f:
                json.dump(archives, f, ensure_ascii=False, indent=4) 