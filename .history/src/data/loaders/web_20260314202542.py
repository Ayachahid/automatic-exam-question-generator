from .base import BaseLoader
import requests
from bs4 import BeautifulSoup #pip install beautifulsoup4 requests
class WebLoader(BaseLoader):
    def load(self, url):
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        return soup.get_text()