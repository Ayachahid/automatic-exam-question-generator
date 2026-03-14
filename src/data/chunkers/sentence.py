import re
from .base import BaseChunker


class SentenceChunker(BaseChunker):

    def __init__(self, max_sentences: int = 8, min_sentences: int = 3):
        self.max_sentences = max_sentences
        self.min_sentences = min_sentences

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        sentences = self._split_sentences(text.strip())

        if not sentences:
            return [text.strip()]

        chunks = []
        current = []

        for sentence in sentences:
            current.append(sentence)
            if len(current) >= self.max_sentences:
                chunks.append(" ".join(current))
                current = current[-self.min_sentences:]

        if current:
            chunks.append(" ".join(current))

        return chunks

    def _split_sentences(self, text: str) -> list[str]:
        try:
            import nltk
            try:
                return nltk.sent_tokenize(text)
            except LookupError:
                nltk.download("punkt", quiet=True)
                return nltk.sent_tokenize(text)
        except ImportError:
            return self._simple_split(text)

    def _simple_split(self, text: str) -> list[str]:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        return [s.strip() for s in sentences if s.strip()]