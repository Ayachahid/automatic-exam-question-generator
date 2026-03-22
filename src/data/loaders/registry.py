from .base import BaseLoader
from .txt import TXTLoader
from .docx import DOCXLoader
from .pdf import PDFLoader
from .pptx import PPTXLoader
from .web import WebLoader
from pathlib import Path
from src.core.exceptions import UnsupportedFormatError


class LoaderFactory:
    def get_loader(self, file_path: str) -> BaseLoader:
        # URL web — vérifier AVANT l'extension
        if file_path.startswith("http://") or file_path.startswith("https://"):
            return WebLoader()

        ext = Path(file_path).suffix.lower()
        if ext == ".txt":
            return TXTLoader()
        if ext == ".docx":
            return DOCXLoader()
        if ext == ".pdf":
            return PDFLoader()
        if ext == ".pptx":
            return PPTXLoader()

        raise UnsupportedFormatError(ext)
