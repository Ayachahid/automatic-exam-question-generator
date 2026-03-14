from .base import BaseLoader
from .txt import TXTLoader
from .docx import DOCXLoader
from .pdf import PDFLoader
from .pptx import PPTXLoader
from .web import WebLoader
from pathlib import Path

class LoaderFactory:
    def get_loader(self, file_path: str) -> BaseLoader:
        ext = Path(file_path).suffix.lower()
        if ext == ".txt":   return TXTLoader()
        if ext == ".docx":  return DOCXLoader()
        if ext == ".pdf":   return PDFLoader()
        #if ext == ".pptx":  return PPTXLoader()
        if file_path.startswith("http://") or file_path.startswith("https://"):
            return WebLoader()
        raise ValueError(f"Unsupported file format: {ext}")