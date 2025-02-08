import json
import os
from pathlib import Path
import logging

class UserArchiveManager:
    def __init__(self):
        self.archive_paths_file = "user_archives.json"
        # Создаем файл, если он не существует
        if not os.path.exists(self.archive_paths_file):
            with open(self.archive_paths_file, 'w', encoding='utf-8') as f:
                json.dump({}, f)

    def add_user_archive(self, user_id, archive_path):
        try:
            with open(self.archive_paths_file, 'r', encoding='utf-8') as f:
                archives = json.load(f)
        except json.JSONDecodeError:
            archives = {}  # Если файл пустой или поврежден, начинаем с пустого словаря
            
        user_id = str(user_id)
        print("add", user_id)
        logging.info(f"Adding archive path for user {user_id}: {archive_path}")
        archives[user_id] = archive_path
        
        with open(self.archive_paths_file, 'w', encoding='utf-8') as f:
            json.dump(archives, f, ensure_ascii=False, indent=4)
        
        # Проверяем, что путь сохранился
        logging.info(f"Current archives: {archives}")

    def get_user_archive_path(self, user_id):
        try:
            with open(self.archive_paths_file, 'r', encoding='utf-8') as f:
                archives = json.load(f)
                user_id = str(user_id)
                path = archives.get(user_id)
                logging.info(f"Getting archive path for user {user_id}. Available users: {list(archives.keys())}")
                return path
        except (json.JSONDecodeError, FileNotFoundError):
            return None

    def remove_user_archive(self, user_id: str):
        """Удаляет информацию об архиве пользователя"""
        with open(self.archive_paths_file, 'r', encoding='utf-8') as f:
            archives = json.load(f)
        
        if str(user_id) in archives:
            del archives[str(user_id)]
            
            with open(self.archive_paths_file, 'w', encoding='utf-8') as f:
                json.dump(archives, f, ensure_ascii=False, indent=4) 