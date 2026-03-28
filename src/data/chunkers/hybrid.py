import numpy as np
from src.core.exceptions import InvalidChunkConfigError
from .base import BaseChunker
from .fixed_size import FixedSizeChunker


class HybridChunker(BaseChunker):

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        similarity_threshold: float = 0.75,
        max_chunk_size: int = 1200,
        min_chunk_size: int = 150,
        overlap: int = 80,
    ):
        if min_chunk_size >= max_chunk_size:
            raise InvalidChunkConfigError(
                f"min_chunk_size ({min_chunk_size}) must be less than "
                f"max_chunk_size ({max_chunk_size})"
            )
        if overlap >= max_chunk_size:
            raise InvalidChunkConfigError(
                f"overlap ({overlap}) must be less than "
                f"max_chunk_size ({max_chunk_size})"
            )

        self.model_name = model_name
        self.similarity_threshold = similarity_threshold
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
        self.overlap = overlap
        self.model = None

        # fixed-size pre-split
        self._fixed_chunker = FixedSizeChunker(
            chunk_size=max_chunk_size,
            overlap=overlap,
        )

    # public API

    def chunk(self, text: str) -> list[str]:
        """
        Split text using the hybrid strategy.

        Args:
            text: Raw cleaned text to chunk.

        Returns:
            List of text chunks respecting size and semantic boundaries.
        """
        if not text or not text.strip():
            return []

        #  fixed-size split
        fixed_chunks = self._fixed_chunker.chunk(text.strip())

        if len(fixed_chunks) <= 1:
            return fixed_chunks

        # load sentence-transformers model
        self._load_model()

        #  embed all fixed chunks
        embeddings: list[np.ndarray] = list(self.model.encode(fixed_chunks))

        #  semantic merging
        merged = self._semantic_merge(fixed_chunks, embeddings)

        return merged

    # private helpers

    def _load_model(self) -> None:
        """Lazy-load the SentenceTransformer model."""
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer

                self.model = SentenceTransformer(self.model_name)
            except ImportError:
                raise ImportError(
                    "sentence-transformers is required for HybridChunker. "
                    "Install with: pip install sentence-transformers"
                )

    def _semantic_merge(
        self,
        chunks: list[str],
        embeddings: list[np.ndarray],
    ) -> list[str]:

        result: list[str] = []
        current_text = chunks[0]
        current_embedding = embeddings[0]

        for i in range(1, len(chunks)):
            next_text = chunks[i]
            next_embedding = embeddings[i]

            merged_text = current_text + " " + next_text
            merged_len = len(merged_text)

            sim = self._cosine_similarity(current_embedding, next_embedding)

            # Merge conditions:
            #   - current chunk is too short (below min_chunk_size), OR
            #   - chunks are semantically similar
            # But only if the merged result stays within max_chunk_size.
            should_merge = (
                len(current_text) < self.min_chunk_size
                or sim >= self.similarity_threshold
            ) and merged_len <= self.max_chunk_size

            if should_merge:
                # Merge: update current chunk with averaged embedding
                current_text = merged_text
                current_embedding = np.mean([current_embedding, next_embedding], axis=0)
            else:
                result.append(current_text)
                current_text = next_text
                current_embedding = next_embedding

        # Append the last remaining chunk
        if current_text:
            result.append(current_text)

        return result

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity between two vectors."""
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))
