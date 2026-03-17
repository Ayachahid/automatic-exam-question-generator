from .base import BaseLoader
from pptx import Presentation
from src.core.exceptions import FileReadError, EmptyDocumentError

class PPTXLoader(BaseLoader):
 
    def load(self, file_path: str) -> str:
        try:
            prs        = Presentation(file_path)
            text_parts = []
 
            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text.strip():
                        text_parts.append(shape.text)
 
            result = "\n".join(text_parts)
        
        except Exception as e:
            raise FileReadError(str(file_path), str(e))
 
        if not result.strip():
            raise EmptyDocumentError(file_path)
 
        return result


