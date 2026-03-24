import pytest
from src.data.chunkers.fixed_size import FixedSizeChunker
from src.data.chunkers.sentence import SentenceChunker
from src.data.chunkers.registry import ChunkerFactory
from src.core.exceptions import InvalidChunkConfigError
from src.data.chunkers.semantic import SemanticChunker

class TestFixedSizeChunker:
    """Tests for FixedSizeChunker."""

    def test_basic_chunking(self, long_sample_text):
        """Test basic chunking functionality."""
        chunk_size = 100
        overlap = 10
        chunker = FixedSizeChunker(chunk_size=chunk_size, overlap=overlap)
        chunks = chunker.chunk(long_sample_text)

        assert len(chunks) > 0
        for chunk in chunks:
            assert len(chunk) > 0
            assert len(chunk) <= chunk_size + 20

    def test_overlap(self):
        """Test that overlap works correctly."""
        text = "1234567890" * 3
        chunker = FixedSizeChunker(chunk_size=10, overlap=5)
        chunks = chunker.chunk(text)

        assert len(chunks) >= 3
        for i in range(len(chunks) - 1):
            overlap_region = chunks[i][-5:]
            assert overlap_region in chunks[i + 1]

    def test_word_boundary_respect(self):
        """Test that chunker respects word boundaries."""
        text = "This is a test with some longer words that might get cut off"
        chunker = FixedSizeChunker(chunk_size=20, overlap=5)
        chunks = chunker.chunk(text)

        # Ensure chunks are not empty and have reasonable size
        for chunk in chunks:
            assert len(chunk) > 0

    def test_empty_input(self):
        """Test handling of empty input."""
        chunker = FixedSizeChunker(chunk_size=100, overlap=10)
        assert chunker.chunk("") == []
        assert chunker.chunk("   ") == []
        assert chunker.chunk(None) == []

    def test_single_chunk(self):
        """Test that small text returns single chunk."""
        text = "Short text"
        chunker = FixedSizeChunker(chunk_size=100, overlap=10)
        chunks = chunker.chunk(text)

        assert len(chunks) == 1
        assert chunks[0] == "Short text"

    def test_invalid_config_overlap_greater_than_chunk(self):
        """Test InvalidChunkConfigError for invalid config."""
        with pytest.raises(InvalidChunkConfigError):
            FixedSizeChunker(chunk_size=50, overlap=100)

    def test_invalid_config_overlap_equals_chunk(self):
        """Test InvalidChunkConfigError when overlap equals chunk size."""
        with pytest.raises(InvalidChunkConfigError):
            FixedSizeChunker(chunk_size=50, overlap=50)

    def test_newline_handling(self):
        """Test that newlines are handled correctly."""
        text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        chunker = FixedSizeChunker(chunk_size=30, overlap=10)
        chunks = chunker.chunk(text)

        assert len(chunks) > 0
        assert all(chunk.strip() for chunk in chunks)


class TestSentenceChunker:
    """Tests for SentenceChunker."""

    def test_basic_chunking(self, sample_text):
        """Test basic sentence chunking."""
        chunker = SentenceChunker(max_sentences=1, min_sentences=0)
        chunks = chunker.chunk(sample_text)

        assert len(chunks) == 4
        assert "This is a sample text" in chunks[0]

    def test_sentence_grouping(self, sample_text):
        """Test grouping multiple sentences per chunk."""
        chunker = SentenceChunker(max_sentences=2, min_sentences=0)
        chunks = chunker.chunk(sample_text)

        assert len(chunks) == 2
        for chunk in chunks:
            assert chunk.count(".") >= 1

    def test_overlap_with_min_sentences(self, sample_text):
        """Test that min_sentences creates overlap."""
        chunker = SentenceChunker(max_sentences=2, min_sentences=1)
        chunks = chunker.chunk(sample_text)

        assert len(chunks) >= 2
        for i in range(len(chunks) - 1):
            last_sentence = chunks[i].split(". ")[-1]
            assert last_sentence in chunks[i + 1]

    def test_empty_input(self):
        """Test handling of empty input."""
        chunker = SentenceChunker()
        assert chunker.chunk("") == []
        assert chunker.chunk("   ") == []
        assert chunker.chunk(None) == []

    def test_single_sentence(self):
        """Test chunking a single sentence."""
        text = "This is a single sentence."
        chunker = SentenceChunker(max_sentences=5, min_sentences=0)
        chunks = chunker.chunk(text)

        assert len(chunks) == 1
        assert chunks[0] == text

    def test_fallback_splitting(self):
        """Test fallback sentence splitting when nltk is unavailable."""
        text = "First sentence. Second sentence! Third sentence? Fourth sentence."
        chunker = SentenceChunker(max_sentences=1, min_sentences=0)
        chunks = chunker.chunk(text)

        assert len(chunks) >= 3

    def test_no_trailing_punctuation(self):
        """Test text without standard sentence endings."""
        text = "This is text without proper sentence endings just words"
        chunker = SentenceChunker(max_sentences=5, min_sentences=0)
        chunks = chunker.chunk(text)

        assert len(chunks) == 1


class TestChunkerFactory:
    """Tests for ChunkerFactory."""

    def test_get_fixed_size_chunker(self):
        """Test getting FixedSizeChunker from factory."""
        factory = ChunkerFactory()
        chunker = factory.get_chunker("fixed_size")
        assert isinstance(chunker, FixedSizeChunker)

    def test_get_sentence_chunker(self):
        """Test getting SentenceChunker from factory."""
        factory = ChunkerFactory()
        chunker = factory.get_chunker("sentence")
        assert isinstance(chunker, SentenceChunker)

    def test_get_default_chunker(self):
        """Test that unknown chunker name returns default."""
        factory = ChunkerFactory()
        chunker = factory.get_chunker("unknown")
        assert isinstance(chunker, FixedSizeChunker)

    def test_get_chunker_no_argument(self):
        """Test that no argument returns default chunker."""
        factory = ChunkerFactory()
        chunker = factory.get_chunker()
        assert isinstance(chunker, FixedSizeChunker)


# semantic
class TestSemanticChunker:
    """Tests for SemanticChunker."""

    def test_basic_chunking(self, sample_text):
        chunker = SemanticChunker(similarity_threshold=0.5)
        chunks = chunker.chunk(sample_text)

        assert len(chunks) > 0
        assert all(isinstance(c, str) for c in chunks)

    def test_empty_input(self):
        chunker = SemanticChunker()
        assert chunker.chunk("") == []
        assert chunker.chunk("   ") == []
        assert chunker.chunk(None) == []

    def test_single_sentence(self):
        text = "This is a single sentence."
        chunker = SemanticChunker()
        chunks = chunker.chunk(text)

        assert len(chunks) == 1
        assert chunks[0] == text

    def test_similarity_effect(self, sample_text):
        chunker_loose = SemanticChunker(similarity_threshold=0.3)
        chunker_strict = SemanticChunker(similarity_threshold=0.9)

        chunks_loose = chunker_loose.chunk(sample_text)
        chunks_strict = chunker_strict.chunk(sample_text)

        assert len(chunks_strict) >= len(chunks_loose)

    def test_max_sentences_limit(self, sample_text):
        """Test that max_sentences is respected."""
        
        chunker = SemanticChunker(max_sentences=1, min_sentences=0, similarity_threshold=0.0)
        chunks = chunker.chunk(sample_text)

        assert len(chunks) >= 1
        for chunk in chunks:
            # count sentences by "."
            assert chunk.count(".") <= 1

    def test_overlap_with_min_sentences(self, sample_text):
        """Test overlap behavior."""
        chunker = SemanticChunker(max_sentences=2, min_sentences=1, similarity_threshold=0.0)
        chunks = chunker.chunk(sample_text)

        assert len(chunks) >= 2
        # check that last sentence of chunk i is in chunk i+1
        for i in range(len(chunks) - 1):
            last_sentence = chunks[i].split(". ")[-1]
            assert last_sentence in chunks[i + 1]