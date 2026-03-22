from .base import BaseLoader


class TXTLoader(BaseLoader):

    def load(self, file_path: str) -> str:
        with open(file_path, encoding="utf-8") as f:
            text = f.read()
        return text
