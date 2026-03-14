
from .base import BaseLoader
import fitz  # PyMuPDF

class PDFLoader(BaseLoader):
    def load(self, file_path):
        text = []
        doc = fitz.open(file_path)
        for page in doc:
            text.append(page.get_text())
        return "\n".join(text)