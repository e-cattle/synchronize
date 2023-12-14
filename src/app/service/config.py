import json, os


class Config:
    def __init__(self):
        self._file_name = os.path.abspath(__file__).replace(
            "app/service/config.py", "config.json"
        )
        self.config = {}

    def read_config(self):
        self.config = self.read_files(self._file_name)

    def read_files(self, file_name: str):
        with open(f"{file_name}", "r") as f:
            config = json.load(f)
        return config

    def write_config(self, data):
        with open(f"{self._file_name}", "w") as f:
            json.dump(data, f)
