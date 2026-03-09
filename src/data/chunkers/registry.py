from .fixed_size import FixedSizeChunker

class ChunkerFactory:
    def get_chunker(self):
        return FixedSizeChunker()