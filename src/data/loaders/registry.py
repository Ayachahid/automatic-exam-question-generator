from .base import BaseLoader
from .txt import TXTLoader
from .docx import DOCXLoader
from .pdf import PDFLoader
from .pptx import PPTXLoader
from .web import WebLoader
from pathlib import Path
from src.core.exceptions import UnsupportedFormatError
from src.core.logger import get_logger

logger = get_logger("data.loaders.registry")


class LoaderFactory:
    def get_loader(self, file_path: str) -> BaseLoader:
        logger.info(f"Resolving loader for: {file_path}")
        # URL web — vérifier AVANT l'extension
        if file_path.startswith("http://") or file_path.startswith("https://"):
            logger.info("Selected WebLoader")
            return WebLoader()

        ext = Path(file_path).suffix.lower()
        logger.debug(f"Detected file extension: {ext}")
        if ext == ".txt":
            logger.info("Selected TXTLoader")
            return TXTLoader()
        logger.info("Selected DOCXLoader")
        if ext == ".docx":
            return DOCXLoader()
        if ext == ".pdf":
            logger.info("Selected PDFLoader")
            return PDFLoader()
        if ext == ".pptx":
            logger.info("Selected PPTXLoader")
            return PPTXLoader()

        logger.error(f"Unsupported file format: {ext}")
        raise UnsupportedFormatError(ext)
