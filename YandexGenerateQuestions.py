import os
import time
import requests
from dotenv import load_dotenv


class YandexQuestionGenerator:
    """
    Класс для генерации вопросов по заметке с использованием YandexGPT API.
    """

    def __init__(self, folder_id: str = None, api_key: str = None, model: str = 'yandexgpt-lite',
                 temperature: float = 0.3, max_tokens: int = 4000):
        load_dotenv()
        self.folder_id = folder_id or os.getenv("YANDEX_FOLDER_ID")
        self.api_key = api_key or os.getenv("YANDEX_API_KEY")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        if not self.folder_id or not self.api_key:
            raise ValueError("YANDEX_FOLDER_ID and YANDEX_API_KEY must be provided "
                             "either as arguments or in a .env file.")

        self.base_url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completionAsync"
        self.operation_url = "https://llm.api.cloud.yandex.net:443/operations/{}"
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Api-Key {self.api_key}'
        }


    def generate_questions(self, note: str, user_prompt: str = "F#") -> str:
        system_prompt = (
            "Я хочу, чтобы ты выступил в роли опытного преподавателя и составил "
            "исчерпывающий набор вопросов для проверки знаний по этой заметке. "
            "Твоя задача – создать разнообразные и сложные вопросы, которые позволят "
            "оценить глубину понимания материала: "
        ) + note  # Более читаемая конкатенация


        body = {
            'modelUri': f'gpt://{self.folder_id}/{self.model}',
            'completionOptions': {
                'stream': False,
                'temperature': self.temperature,
                'maxTokens': self.max_tokens
            },
            'messages': [
                {'role': 'system', 'text': system_prompt},
                {'role': 'user', 'text': user_prompt},
            ],
        }

        try:
            response = requests.post(self.base_url, headers=self.headers, json=body)
            response.raise_for_status()
            operation_id = response.json().get('id')
            if not operation_id:
                raise KeyError("Operation ID not found in the initial response.")

            operation_url = self.operation_url.format(operation_id)
            headers_for_status = {"Authorization": f"Api-Key {self.api_key}"}

            while True:
                response = requests.get(operation_url, headers=headers_for_status)
                response.raise_for_status()
                data = response.json()
                if data.get("done"):
                    break
                time.sleep(2)

            if 'response' not in data or 'alternatives' not in data['response'] or len(data['response']['alternatives']) == 0:
                raise KeyError("Unexpected response structure. 'response' or 'alternatives' missing.")

            answer = data['response']['alternatives'][0]['message']['text']

            return answer

        except requests.RequestException as e:
            raise requests.RequestException(f"Request failed: {e}") from e
        except KeyError as e:
            raise KeyError(f"Key error in API response: {e}") from e
        except Exception as e:
             raise Exception(f"An unexpected error occurred: {e}") from e

if __name__ == '__main__':
    generator = YandexQuestionGenerator()
    note_text = "Я хз что писать"
    try:
        questions = generator.generate_questions(note_text)
        print(questions)
    except Exception as e:
        print(f"An error occurred: {e}")