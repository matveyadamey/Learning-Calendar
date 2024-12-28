import json 

class ConfigManager:

    def get_json_value(self,name):
        json_file_path = "config.json"

        with open(json_file_path, 'r') as j:
            json_value= json.loads(j.read())[name]
        return json_value
