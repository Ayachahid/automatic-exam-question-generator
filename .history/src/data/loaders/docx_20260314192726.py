from .base import BaseLoader
from docx import Document


class DOCXLoader(BaseLoader):
    def load(self, file_path):
        doc = Document(file_path)

        text = []
        for paragraph in doc.paragraphs:
            text.append(paragraph.text)

        return "\n".join(text)
    