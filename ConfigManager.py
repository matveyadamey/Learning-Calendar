import json


class ConfigManager:
    def __init__(self, user_id=None):
        self.file_path = "config.json"
        self.user_id = str(user_id) if user_id else None

    def load_data(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            print("Ошибка чтения JSON файла")
            return {}

    def get_json_value(self, name):
        with open(self.file_path, 'r', encoding='utf-8') as j:
            data = json.loads(j.read())
            
            # Если указан user_id, ищем в пользовательских настройках
            if self.user_id and 'users' in data:
                if self.user_id in data['users']:
                    return data['users'][self.user_id].get(name)
            
            # Если не нашли пользовательские настройки или user_id не указан,
            # возвращаем глобальные настройки
            return data.get(name)

    def save_data(self, data):
        try:
            with open(self.file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Ошибка записи в файл: {e}")

    def edit_field(self, field_path, new_value):
        print("editing_field...")
        data = self.load_data()
        
        if not data:
            print("Файл пустой или не существует")
            return
        
        current_level = data
        fields = field_path.split('.')
        target_field = fields[-1]
        
        try:
            for field in fields[:-1]:
                current_level = current_level[field]
            
            if target_field in current_level:
                current_level[target_field] = new_value
                self.save_data(data)
                print(f"Поле {field_path} успешно обновлено")
            else:
                print(f"Поле {target_field} не найдено")
        
        except KeyError:
            print(f"Один из уровней пути {field_path} не существует")
        except TypeError:
            print("Некорректный путь к полю (возможно, попытка индексации несписка)")


