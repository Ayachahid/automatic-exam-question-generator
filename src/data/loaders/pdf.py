from pathlib import Path
from .base import BaseLoader
from src.core.exceptions import FileReadError, EmptyDocumentError
import fitz  # pip install PyMuPDF

class PDFLoader(BaseLoader):

    def load(self, file_path: str) -> str:
        try:
            text = []
            doc = fitz.open(file_path)
            for page in doc:
                text.append(page.get_text())
            doc.close()
            result = "\n".join(text)
            
        except Exception as e:
            raise FileReadError(str(file_path), str(e))
        
        if not result.strip():
            raise EmptyDocumentError(file_path)

        return result