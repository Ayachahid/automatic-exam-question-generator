from .base import BaseLoader
from src.core.exceptions import FileReadError
import requests
from bs4 import BeautifulSoup

class WebLoader(BaseLoader):

    def load(self, url: str):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            soup     = BeautifulSoup(response.text, "html.parser")
        

            # Supprime les balises inutiles
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
 
            text = " ".join(s.strip() for s in soup.stripped_strings)
            return text
 
        except Exception as e:
            raise FileReadError(url, str(e))