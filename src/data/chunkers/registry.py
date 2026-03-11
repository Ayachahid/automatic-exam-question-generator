from .fixed_size import FixedSizeChunker

class ChunkerFactory:
    def get_chunker(self, chunker_name=None):
        if chunker_name == "fixed_size":
            return FixedSizeChunker()
        elif chunker_name == None:
            return FixedSizeChunker()