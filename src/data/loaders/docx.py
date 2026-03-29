from .base import BaseLoader
from src.core.exceptions import FileReadError, EmptyDocumentError
from docx import Document
from src.core.logger import get_logger

logger = get_logger("data.loaders.docx")


class DOCXLoader(BaseLoader):

    def load(self, file_path):
        logger.info(f"Loading DOCX file: {file_path}")
        try:
            doc = Document(file_path)
            text = [p.text for p in doc.paragraphs if p.text.strip()]
            result = "\n".join(text)

            logger.debug(f"Extracted {len(text)} paragraphs")

        except Exception as e:
            logger.exception(f"Error reading DOCX file: {file_path}")
            raise FileReadError(str(file_path), str(e))

        if not result.strip():
            logger.warning(f"Empty document: {file_path}")
            raise EmptyDocumentError(file_path)

        logger.info(f"Successfully loaded DOCX file: {file_path} ({len(result)} chars)")

        return result
