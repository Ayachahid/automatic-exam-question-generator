from .base import BaseLoader
from src.core.exceptions import FileReadError, EmptyDocumentError
import fitz  # pip install PyMuPDF
from src.core.logger import get_logger

logger = get_logger("data.loaders.pdf")


class PDFLoader(BaseLoader):

    def load(self, file_path: str) -> str:
        logger.info(f"Loading PDF file: {file_path}")
        try:
            text = []
            doc = fitz.open(file_path)
            for page in doc:
                text.append(page.get_text())
            doc.close()
            result = "\n".join(text)

            logger.debug(f"Extracted {len(text)} pages from PDF")

        except Exception as e:
            logger.exception(f"Error reading PDF file: {file_path}")
            raise FileReadError(str(file_path), str(e))

        if not result.strip():
            logger.warning(f"Empty PDF document: {file_path}")
            raise EmptyDocumentError(file_path)

        logger.info(f"Successfully loaded PDF file: {file_path} ({len(result)} chars)")

        return result
