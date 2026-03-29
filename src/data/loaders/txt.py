from .base import BaseLoader
from src.core.logger import get_logger

logger = get_logger("data.loaders.txt")


class TXTLoader(BaseLoader):

    def load(self, file_path: str) -> str:
        logger.info(f"Loading TXT file: {file_path}")
        try:
            with open(file_path, encoding="utf-8") as f:
                text = f.read()
            logger.debug(f"TXT file size: {len(text)} chars")

        except Exception:
            logger.exception(f"Error reading TXT file: {file_path}")
            raise
        if not text.strip():
            logger.warning(f"Empty TXT file: {file_path}")

        logger.info(f"Successfully loaded TXT file: {file_path}")

        return text
