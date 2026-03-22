from .base import BaseChunker
from src.core.exceptions import InvalidChunkConfigError


class FixedSizeChunker(BaseChunker):

    def __init__(self, chunk_size=1000, overlap=100):
        if overlap >= chunk_size:
            raise InvalidChunkConfigError(
                f"overlap ({overlap}) doit être inférieur à chunk_size ({chunk_size})"
            )

        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        text = text.strip()
        chunks = []
        start = 0

        while start < len(text):
            end = min(start + self.chunk_size, len(text))

            # Ne pas couper le mot du milieu
            if end < len(text) and text[end] not in (" ", "\n"):
                boundary = text.rfind(" ", start, end)
                if boundary > start:
                    end = boundary

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start += self.chunk_size - self.overlap

        return chunks
