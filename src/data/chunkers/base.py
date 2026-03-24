from abc import ABC, abstractmethod
import re
from typing import List


class BaseChunker(ABC):

    @abstractmethod
    def chunk(self, text: str) -> list[str]:
        raise NotImplementedError

    @staticmethod
    def _split_sentences(text: str) -> List[str]:
        """Split text into sentences using NLTK with fallback to regex."""
        try:
            import nltk

            try:
                return nltk.sent_tokenize(text)
            except LookupError:
                nltk.download("punkt", quiet=True)
                nltk.download("punkt_tab", quiet=True)
                return nltk.sent_tokenize(text)
        except ImportError:
            return BaseChunker._simple_split(text)

    @staticmethod
    def _simple_split(text: str) -> List[str]:
        """Fallback sentence splitting using regex."""
        sentences = re.split(r"(?<=[.!?])\s+", text)
        return [s.strip() for s in sentences if s.strip()]
