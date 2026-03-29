import numpy as np
from src.core.exceptions import InvalidChunkConfigError
from .base import BaseChunker
from .fixed_size import FixedSizeChunker
from src.core.logger import get_logger

logger = get_logger("data.chunkers.hybrid")


class HybridChunker(BaseChunker):

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        similarity_threshold: float = 0.75,
        max_chunk_size: int = 1200,
        min_chunk_size: int = 150,
        overlap: int = 80,
    ):
        logger.info("Initializing HybridChunker")

        if min_chunk_size >= max_chunk_size:
            logger.error("Invalid chunk config: min_chunk_size >= max_chunk_size")
            raise InvalidChunkConfigError(
                f"min_chunk_size ({min_chunk_size}) must be less than "
                f"max_chunk_size ({max_chunk_size})"
            )
        if overlap >= max_chunk_size:
            logger.error("Invalid chunk config: overlap >= max_chunk_size")
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
        logger.info("Starting hybrid chunking")

        if not text or not text.strip():
            logger.warning("Empty text received")
            return []

        #  fixed-size split
        fixed_chunks = self._fixed_chunker.chunk(text.strip())
        logger.info(f"Fixed chunking produced {len(fixed_chunks)} chunks")

        if len(fixed_chunks) <= 1:
            logger.info("Only one chunk, skipping semantic merge")
            return fixed_chunks

        # load sentence-transformers model
        self._load_model()

        #  embed all fixed chunks
        logger.info("Encoding chunks into embeddings")
        embeddings: list[np.ndarray] = list(self.model.encode(fixed_chunks))

        #  semantic merging
        merged = self._semantic_merge(fixed_chunks, embeddings)
        logger.info(f"Semantic merge reduced chunks to {len(merged)}")

        return merged

    # private helpers

    def _load_model(self) -> None:
        """Lazy-load the SentenceTransformer model."""
        if self.model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            try:
                from sentence_transformers import SentenceTransformer

                self.model = SentenceTransformer(self.model_name)
            except ImportError:
                logger.exception("Failed to import sentence-transformers")
                raise ImportError(
                    "sentence-transformers is required for HybridChunker. "
                    "Install with: pip install sentence-transformers"
                )

    def _semantic_merge(
        self,
        chunks: list[str],
        embeddings: list[np.ndarray],
    ) -> list[str]:
        logger.info("Starting semantic merging")

        result: list[str] = []
        current_text = chunks[0]
        current_embedding = embeddings[0]

        for i in range(1, len(chunks)):
            next_text = chunks[i]
            next_embedding = embeddings[i]

            merged_text = current_text + " " + next_text
            merged_len = len(merged_text)

            sim = self._cosine_similarity(current_embedding, next_embedding)

            logger.debug(f"Chunk {i}: similarity={sim:.4f}, size={merged_len}")
            # Merge conditions:
            #   - current chunk is too short (below min_chunk_size), OR
            #   - chunks are semantically similar
            # But only if the merged result stays within max_chunk_size.
            should_merge = (
                len(current_text) < self.min_chunk_size
                or sim >= self.similarity_threshold
            ) and merged_len <= self.max_chunk_size

            if should_merge:
                logger.debug("Merging chunks")
                # Merge: update current chunk with averaged embedding
                current_text = merged_text
                current_embedding = np.mean([current_embedding, next_embedding], axis=0)
            else:
                logger.debug("Keeping chunk separate")
                result.append(current_text)
                current_text = next_text
                current_embedding = next_embedding

        # Append the last remaining chunk
        if current_text:
            result.append(current_text)

        logger.info(f"Semantic merging produced {len(result)} chunks")

        return result

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity between two vectors."""
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            logger.warning("Zero vector encountered in cosine similarity")
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))
