# src/data/loaders/web.py
from .base import BaseLoader
import requests
from bs4 import BeautifulSoup

class WebLoader(BaseLoader):
    def load(self, url: str):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        # Extract all visible text
        text = ' '.join(s.strip() for s in soup.stripped_strings)
        return text