from .base import BaseLoader

class TXTLoader(BaseLoader):
    def load(self, file_path):
        with open(file_path) as f:
            text = f.read()
        return text