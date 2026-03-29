from .base import BaseLoader
from src.core.exceptions import FileReadError
import requests
from bs4 import BeautifulSoup
from src.core.logger import get_logger

logger = get_logger("data.loaders.web")


class WebLoader(BaseLoader):

    def load(self, url: str):
        logger.info(f"Fetching URL: {url}")
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Supprime les balises inutiles
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()

            text = " ".join(s.strip() for s in soup.stripped_strings)
            logger.debug(f"Extracted web text length: {len(text)} chars")
            logger.info(f"Successfully fetched URL: {url}")

            return text

        except Exception as e:
            logger.exception(f"Error fetching URL: {url}")
            raise FileReadError(url, str(e))
