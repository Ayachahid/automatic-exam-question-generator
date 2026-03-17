from .base import BaseLoader
from src.core.exceptions import FileReadError, EmptyDocumentError
from docx import Document


class DOCXLoader(BaseLoader):
    
    def load(self, file_path):
        try:
            doc = Document(file_path)
            text   = [p.text for p in doc.paragraphs if p.text.strip()]
            result = "\n".join(text)

        except Exception as e:
            raise FileReadError(str(file_path), str(e))
        
        if not result.strip():
            raise EmptyDocumentError(file_path)

        return result
    