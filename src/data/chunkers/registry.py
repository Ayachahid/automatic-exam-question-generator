from .fixed_size import FixedSizeChunker
from .sentence import SentenceChunker
from .semantic import SemanticChunker
from .hybrid import HybridChunker
from src.core.logger import get_logger

logger = get_logger("data.chunkers.registry")


class ChunkerFactory:
    def get_chunker(
        self,
        chunker_name: str = "fixed_size",
        chunk_size: int = 1000,
        overlap: int = 100,
        model_name: str = "all-MiniLM-L6-v2",
        similarity_threshold: float = 0.75,
        max_sentences: int = 8,
        min_sentences: int = 3,
        batch_size: int = 64,
    ):
        logger.info(f"Requested chunker: {chunker_name}")

        if chunker_name == "fixed_size":
            logger.info("Using FixedSizeChunker")
            return FixedSizeChunker(chunk_size=chunk_size, overlap=overlap)
        elif chunker_name == "sentence":
            logger.info("Using SentenceChunker")
            return SentenceChunker(
                max_sentences=max_sentences, min_sentences=min_sentences
            )
        elif chunker_name == "semantic":
            logger.info("Using SemanticChunker")
            return SemanticChunker(
                model_name=model_name,
                similarity_threshold=similarity_threshold,
                max_sentences=max_sentences,
                min_sentences=min_sentences,
                batch_size=batch_size,
            )
        elif chunker_name == "hybrid":
            logger.info("Using HybridChunker")
            return HybridChunker()
        else:
            logger.warning(
                f"Unknown chunker '{chunker_name}', falling back to FixedSizeChunker"
            )
            logger.info("Using FixedSizeChunker")
            return FixedSizeChunker(chunk_size=chunk_size, overlap=overlap)
