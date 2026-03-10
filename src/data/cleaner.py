class TextCleaner:
    def clean(self, text: str) -> str:
        # text = re.sub(r'\x0c', ' ', text)           # remove form feeds
        # text = re.sub(r'Page \d+ of \d+', '', text) # remove page numbers
        # text = re.sub(r'\s+', ' ', text)             # collapse whitespace
        # text = text.strip()
        return text