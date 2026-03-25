from .fixed_size import FixedSizeChunker
from .sentence import SentenceChunker
from .semantic import SemanticChunker

# from .hybrid import HybridChunker


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
        if chunker_name == "fixed_size":
            return FixedSizeChunker(chunk_size=chunk_size, overlap=overlap)
        elif chunker_name == "sentence":
            return SentenceChunker(
                max_sentences=max_sentences, min_sentences=min_sentences
            )
        elif chunker_name == "semantic":
            return SemanticChunker(
                model_name=model_name,
                similarity_threshold=similarity_threshold,
                max_sentences=max_sentences,
                min_sentences=min_sentences,
                batch_size=batch_size,
            )
        # elif chunker_name == "hybrid":
        #     return HybridChunker()
        else:
            return FixedSizeChunker(chunk_size=chunk_size, overlap=overlap)
