from .base import BaseChunker
from src.core.logger import get_logger
import re

logger = get_logger("data.chunkers.sentence")


class SentenceChunker(BaseChunker):

    def __init__(self, max_sentences: int = 8, min_sentences: int = 3):
        self.max_sentences = max_sentences
        self.min_sentences = min_sentences
        logger.debug(
            f"SentenceChunker initialized: max_sentences={max_sentences} min_sentences={min_sentences}"
        )

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            logger.debug("Empty input — returning []")
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
                if self.min_sentences > 0:
                    current = current[-self.min_sentences :]
                else:
                    current = []

        if current:
            chunks.append(" ".join(current))
        logger.debug(
            f"SentenceChunker produced {len(chunks)} chunks from {len(sentences)} sentences"
        )

        return chunks

    def _split_sentences(self, text: str) -> list[str]:
        try:
            import nltk

            try:
                return nltk.sent_tokenize(text)
            except LookupError:
                logger.warning("NLTK punkt not found — downloading...")
                nltk.download("punkt", quiet=True)
                nltk.download("punkt_tab", quiet=True)
                return nltk.sent_tokenize(text)
        except ImportError:
            logger.warning("NLTK not available — using regex fallback")
            return self._simple_split(text)

    def _simple_split(self, text: str) -> list[str]:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        return [s.strip() for s in sentences if s.strip()]
