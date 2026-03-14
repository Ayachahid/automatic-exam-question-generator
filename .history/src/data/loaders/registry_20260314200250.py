from .base import BaseLoader
from .txt import TXTLoader
from .docx import DOCXLoader
from pathlib import Path

class LoaderFactory:
    def get_loader(self, file_path: str) -> BaseLoader:
        return TXTLoader()
         ext = Path(file_path).suffix.lower()
    #     if ext == ".pdf":   return PDFLoader()
    #
     if ext == ".docx":  return DocxLoader()
    #     if ext == ".pptx":  return PptxLoader()
    #     if ext == ".txt":   return TxtLoader()
         raise ValueError(f"Unsupported file format: {ext}")
    
    def get_TXTLoader(self):
        return TXTLoader()