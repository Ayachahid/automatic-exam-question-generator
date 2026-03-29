import numpy as np
from typing import List
from .base import BaseChunker
from src.core.exceptions import InvalidChunkConfigError
from src.core.logger import get_logger

logger = get_logger("data.chunkers.semantic")


class SemanticChunker(BaseChunker):
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        similarity_threshold: float = 0.75,
        max_sentences: int = 8,
        min_sentences: int = 3,
        batch_size: int = 64,
    ):
        if min_sentences >= max_sentences:
            raise InvalidChunkConfigError(
                "min_sentences must be less than max_sentences"
            )

        self.model_name = model_name
        self.similarity_threshold = similarity_threshold
        self.max_sentences = max_sentences
        self.min_sentences = min_sentences
        self.batch_size = batch_size
        self.model = None
        logger.debug(
            f"SemanticChunker initialized: model={model_name} threshold={similarity_threshold}"
        )

    def _load_model(self) -> None:
        if self.model is None:
            logger.info(f"Loading SentenceTransformer model: {self.model_name}")
            try:
                from sentence_transformers import SentenceTransformer

                self.model = SentenceTransformer(self.model_name)
                logger.info("SentenceTransformer model loaded successfully")
            except ImportError:
                raise ImportError(
                    "sentence-transformers is required for SemanticChunker. "
                    "Install with: pip install sentence-transformers"
                )

    def chunk(self, text: str) -> List[str]:
        if not text or not text.strip():
            logger.debug("Empty input — returning []")
            return []

        sentences = self._split_sentences(text.strip())
        if not sentences:
            return [text.strip()]

        self._load_model()

        # Encode in batches for long texts
        embeddings: List[np.ndarray] = []
        for i in range(0, len(sentences), self.batch_size):
            batch = sentences[i : i + self.batch_size]
            batch_embeddings = self.model.encode(batch)
            embeddings.extend(batch_embeddings)

        chunks: List[str] = []
        current: List[str] = [sentences[0]]

        for i in range(1, len(sentences)):
            # Compare current sentence against the mean embedding of the chunk
            chunk_mean_embedding = np.mean(embeddings[: len(current)], axis=0)
            sim = self._cosine_similarity(chunk_mean_embedding, embeddings[i])

            # Check if we should start a new chunk
            should_split = (
                sim < self.similarity_threshold or len(current) >= self.max_sentences
            )

            if should_split:
                chunks.append(" ".join(current))
                # Overlap: keep last min_sentences for continuity
                if self.min_sentences > 0 and len(current) >= self.min_sentences:
                    current = current[-self.min_sentences :]
                else:
                    current = []
                current.append(sentences[i])
            else:
                current.append(sentences[i])

        if current:
            chunks.append(" ".join(current))
        logger.debug(
            f"SemanticChunker produced {len(chunks)} chunks from {len(sentences)} sentences"
        )

        return chunks

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))
