from .fixed_size import FixedSizeChunker
from .sentence   import SentenceChunker
#from .semantic   import SemanticChunker
#from .hybrid     import HybridChunker

class ChunkerFactory:
    def get_chunker(self, chunker_name: str = "fixed_size"):
        if chunker_name == "fixed_size":
            return FixedSizeChunker()
        elif chunker_name == "sentence":
            return SentenceChunker()
        elif chunker_name == "semantic":
            return SemanticChunker()
        elif chunker_name == "hybrid":
            return HybridChunker()
        else:
            return FixedSizeChunker()