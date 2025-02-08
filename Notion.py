import requests

class NotionManager:
    def __init__(self, notion_token, database_id):
        """
        Инициализация менеджера Notion.
        
        :param notion_token: Токен авторизации для Notion API.
        :param database_id: ID базы данных, содержащей заметки.
        """
        self.notion_token = notion_token
        self.database_id = database_id
        self.headers = {
            "Authorization": f"Bearer {self.notion_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"  # Версия API
        }

    def fetch_notes(self):
        """
        Получает список заметок из базы данных Notion.
        
        :return: Список заметок в формате JSON.
        """
        url = f"https://api.notion.com/v1/databases/{self.database_id}/query"
        response = requests.post(url, headers=self.headers)

        if response.status_code != 200:
            raise Exception(f"Ошибка при получении данных из Notion: {response.text}")

        data = response.json()
        notes = []

        for result in data.get("results", []):
            properties = result.get("properties", {})
            title = properties.get("Name", {}).get("title", [{}])[0].get("text", {}).get("content", "Без названия")
            created_time = result.get("created_time", "Дата неизвестна")
            notes.append({
                "title": title,
                "created_time": created_time
            })

        return notes


# Пример использования
if __name__ == "__main__":
    # Замените эти значения на свои данные
    NOTION_TOKEN = "your_notion_integration_token"
    DATABASE_ID = "your_database_id"

    # Инициализация менеджера Notion
    notion_manager = NotionManager(NOTION_TOKEN, DATABASE_ID)

    try:
        # Получение списка заметок
        notes = notion_manager.fetch_notes()
        print("Список заметок:")
        for note in notes:
            print(f"Название: {note['title']}, Дата создания: {note['created_time']}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")