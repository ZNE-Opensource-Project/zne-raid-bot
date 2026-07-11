import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.json')

class JsonDB:
    def __init__(self):
        self.data = {}
        if os.path.exists(DB_PATH):
            with open(DB_PATH, 'r') as f:
                self.data = json.load(f)

    def get(self, key):
        return self.data.get(key)

    def set(self, key, value):
        self.data[key] = value
        with open(DB_PATH, 'w') as f:
            json.dump(self.data, f)

db = JsonDB()
