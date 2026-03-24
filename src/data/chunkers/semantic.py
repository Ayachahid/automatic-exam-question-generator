import numpy as np
from .base import BaseChunker

class SemanticChunker(BaseChunker):
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        similarity_threshold: float = 0.75,
        max_sentences: int = 8,
        min_sentences: int = 3,
        batch_size: int = 64,  # for long texts
    ):
        if min_sentences >= max_sentences:
            raise ValueError("min_sentences must be less than max_sentences")
        
        self.similarity_threshold = similarity_threshold
        self.max_sentences = max_sentences
        self.min_sentences = min_sentences
        self.model_name = model_name
        self.model = None
        self.batch_size = batch_size

    def _load_model(self):
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(self.model_name)
            except ImportError:
                raise ImportError("sentence-transformers is required for SemanticChunker")

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        sentences = self._split_sentences(text.strip())
        if not sentences:
            return [text.strip()]

        self._load_model()

        # Encode in batches for long texts
        embeddings = []
        for i in range(0, len(sentences), self.batch_size):
            batch = sentences[i:i+self.batch_size]
            embeddings.extend(self.model.encode(batch))

        chunks = []
        current = [sentences[0]]

        for i in range(1, len(sentences)):
            sim = self._cosine_similarity(embeddings[i - 1], embeddings[i])

            if sim >= self.similarity_threshold and len(current) < self.max_sentences:
                current.append(sentences[i])
            else:
                chunks.append(" ".join(current))
                current = current[-self.min_sentences:] if self.min_sentences > 0 else []
                current.append(sentences[i])

        if current:
            chunks.append(" ".join(current))

        return chunks

    def _cosine_similarity(self, a, b):
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return np.dot(a, b) / (norm_a * norm_b)

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
        import re
        sentences = re.split(r"(?<=[.!?])\s+", text)
        return [s.strip() for s in sentences if s.strip()]