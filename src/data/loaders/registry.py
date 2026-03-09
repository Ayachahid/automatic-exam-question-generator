from .base import BaseLoader
from .txt import TXTLoader
from pathlib import Path

class LoaderFactory:
    def get_loader(self, file_path: str) -> BaseLoader:
        ext = Path(file_path).suffix.lower()
        if ext == '.txt': return TXTLoader()
        return None

    def get_TXTLoader(self):
        return TXTLoader()