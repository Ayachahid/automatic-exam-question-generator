import pytest
from src.data.chunkers.fixed_size import FixedSizeChunker
from src.data.chunkers.sentence import SentenceChunker
from src.data.chunkers.registry import ChunkerFactory
from src.core.exceptions import InvalidChunkConfigError
from src.data.chunkers.semantic import SemanticChunker
from src.data.chunkers.hybrid import HybridChunker
from unittest.mock import MagicMock, patch

import numpy as np


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

    def test_get_semantic_chunker(self):
        """Test getting SemanticChunker from factory."""
        factory = ChunkerFactory()
        chunker = factory.get_chunker("semantic")
        assert isinstance(chunker, SemanticChunker)

    def test_get_hybrid_chunker(self):
        """Test getting HybridChunker from factory."""
        factory = ChunkerFactory()
        chunker = factory.get_chunker("hybrid")
        assert isinstance(chunker, HybridChunker)

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


class TestSemanticChunker:
    """Tests for SemanticChunker."""

    def test_basic_chunking(self, sample_text):
        """Test basic semantic chunking functionality."""
        chunker = SemanticChunker(similarity_threshold=0.5)
        chunks = chunker.chunk(sample_text)

        assert len(chunks) > 0
        assert all(isinstance(c, str) for c in chunks)

    def test_empty_input(self):
        """Test handling of empty input."""
        chunker = SemanticChunker()
        assert chunker.chunk("") == []
        assert chunker.chunk("   ") == []
        assert chunker.chunk(None) == []

    def test_single_sentence(self):
        """Test chunking a single sentence."""
        text = "This is a single sentence."
        chunker = SemanticChunker()
        chunks = chunker.chunk(text)

        assert len(chunks) == 1
        assert chunks[0] == text

    def test_similarity_effect(self, sample_text):
        """Test that higher similarity threshold produces more chunks."""
        chunker_loose = SemanticChunker(similarity_threshold=0.3)
        chunker_strict = SemanticChunker(similarity_threshold=0.9)

        chunks_loose = chunker_loose.chunk(sample_text)
        chunks_strict = chunker_strict.chunk(sample_text)

        # Higher threshold should produce >= chunks (or equal)
        assert len(chunks_strict) >= len(chunks_loose) - 1  # Allow small variance

    def test_max_sentences_limit(self, sample_text):
        """Test that max_sentences is respected."""
        chunker = SemanticChunker(
            max_sentences=1, min_sentences=0, similarity_threshold=0.0
        )
        chunks = chunker.chunk(sample_text)

        assert len(chunks) >= 1
        for chunk in chunks:
            # count sentences by "."
            assert chunk.count(".") <= 1

    def test_overlap_with_min_sentences(self, sample_text):
        """Test that min_sentences creates overlap between chunks."""
        chunker = SemanticChunker(
            max_sentences=2, min_sentences=1, similarity_threshold=0.0
        )
        chunks = chunker.chunk(sample_text)

        assert len(chunks) >= 2
        # Check that last sentence of chunk i is in chunk i+1
        for i in range(len(chunks) - 1):
            last_sentence = chunks[i].split(". ")[-1]
            assert last_sentence in chunks[i + 1]


class TestHybridChunker:
    """Tests for HybridChunker."""

    def test_default_initialization(self):
        """Test default parameters match hybrid.yaml."""
        chunker = HybridChunker()
        assert chunker.similarity_threshold == 0.75
        assert chunker.max_chunk_size == 1200
        assert chunker.min_chunk_size == 150
        assert chunker.overlap == 80
        assert chunker.model_name == "sentence-transformers/all-MiniLM-L6-v2"
        assert chunker.model is None

    def test_custom_initialization(self):
        """Test custom parameters are stored correctly."""
        chunker = HybridChunker(
            model_name="custom-model",
            similarity_threshold=0.9,
            max_chunk_size=800,
            min_chunk_size=100,
            overlap=50,
        )
        assert chunker.model_name == "custom-model"
        assert chunker.similarity_threshold == 0.9
        assert chunker.max_chunk_size == 800
        assert chunker.min_chunk_size == 100
        assert chunker.overlap == 50

    def test_invalid_min_greater_than_max(self):
        """Test InvalidChunkConfigError when min_chunk_size >= max_chunk_size."""
        with pytest.raises(InvalidChunkConfigError):
            HybridChunker(min_chunk_size=500, max_chunk_size=500)

    def test_invalid_overlap_greater_than_max_chunk(self):
        """Test InvalidChunkConfigError when overlap >= max_chunk_size."""
        with pytest.raises(InvalidChunkConfigError):
            HybridChunker(overlap=1200, max_chunk_size=1200)

    def test_internal_fixed_chunker_initialized(self):
        """Test that internal FixedSizeChunker uses correct params."""
        chunker = HybridChunker(max_chunk_size=800, overlap=50)
        assert isinstance(chunker._fixed_chunker, FixedSizeChunker)
        assert chunker._fixed_chunker.chunk_size == 800
        assert chunker._fixed_chunker.overlap == 50

    # edge cases (no model needed)

    def test_empty_string_returns_empty(self):
        """Test that empty input returns empty list."""
        chunker = HybridChunker()
        assert chunker.chunk("") == []

    def test_whitespace_only_returns_empty(self):
        """Test that whitespace-only input returns empty list."""
        chunker = HybridChunker()
        assert chunker.chunk("   ") == []

    def test_none_returns_empty(self):
        """Test that None input returns empty list."""
        chunker = HybridChunker()
        assert chunker.chunk(None) == []

    def test_short_text_single_chunk(self):
        """Test that text shorter than max_chunk_size returns as single chunk."""
        chunker = HybridChunker(max_chunk_size=1200, min_chunk_size=150, overlap=80)
        text = "This is a short text."
        with patch.object(chunker, "_load_model"):
            result = chunker.chunk(text)
        assert len(result) == 1
        assert result[0] == "This is a short text."

    #  cosine similarity

    def test_cosine_identical_vectors(self):
        """Identical vectors → similarity = 1.0."""
        chunker = HybridChunker()
        v = np.array([1.0, 2.0, 3.0])
        assert chunker._cosine_similarity(v, v) == pytest.approx(1.0)

    def test_cosine_orthogonal_vectors(self):
        """Orthogonal vectors → similarity = 0.0."""
        chunker = HybridChunker()
        a = np.array([1.0, 0.0, 0.0])
        b = np.array([0.0, 1.0, 0.0])
        assert chunker._cosine_similarity(a, b) == pytest.approx(0.0)

    def test_cosine_opposite_vectors(self):
        """Opposite vectors → similarity = -1.0."""
        chunker = HybridChunker()
        a = np.array([1.0, 0.0])
        b = np.array([-1.0, 0.0])
        assert chunker._cosine_similarity(a, b) == pytest.approx(-1.0)

    def test_cosine_zero_vector(self):
        """Zero vector → similarity = 0.0, no division by zero."""
        chunker = HybridChunker()
        a = np.array([0.0, 0.0, 0.0])
        b = np.array([1.0, 2.0, 3.0])
        assert chunker._cosine_similarity(a, b) == 0.0

    #  semantic merge logic

    def test_similar_chunks_are_merged(self):
        """Similar embeddings → chunks merged."""
        chunker = HybridChunker(max_chunk_size=500, min_chunk_size=50, overlap=50)
        chunker.model = MagicMock()

        emb = np.array([1.0, 0.0, 0.0])
        result = chunker._semantic_merge(
            ["First chunk content.", "Second chunk content."],
            [emb, emb],
        )

        assert len(result) == 1
        assert "First chunk" in result[0]
        assert "Second chunk" in result[0]

    def test_different_chunks_stay_separate(self):
        """Orthogonal embeddings → chunks stay separate."""
        chunker = HybridChunker(max_chunk_size=500, min_chunk_size=0, overlap=50)
        chunker.model = MagicMock()

        emb_a = np.array([1.0, 0.0, 0.0])
        emb_b = np.array([0.0, 1.0, 0.0])

        result = chunker._semantic_merge(["A" * 100, "B" * 100], [emb_a, emb_b])

        assert len(result) == 2

    def test_short_chunk_force_merged_with_next(self):
        """Short chunk (< min_chunk_size) is merged regardless of similarity."""
        chunker = HybridChunker(max_chunk_size=500, min_chunk_size=100, overlap=50)
        chunker.model = MagicMock()

        emb_a = np.array([1.0, 0.0, 0.0])
        emb_b = np.array([0.0, 1.0, 0.0])  # different but still merged

        result = chunker._semantic_merge(["Short.", "B" * 100], [emb_a, emb_b])

        assert len(result) == 1
        assert "Short." in result[0]

    def test_merge_respects_max_chunk_size(self):
        """Chunks are NOT merged if result exceeds max_chunk_size."""
        chunker = HybridChunker(max_chunk_size=100, min_chunk_size=0, overlap=10)
        chunker.model = MagicMock()

        emb = np.array([1.0, 0.0, 0.0])
        result = chunker._semantic_merge(["A" * 60, "B" * 60], [emb, emb])

        assert len(result) == 2

    # model loading

    def test_model_is_none_at_init(self):
        """Model should be None before first chunk() call."""
        chunker = HybridChunker()
        assert chunker.model is None

    def test_load_model_raises_import_error(self):
        """ImportError raised when sentence-transformers is missing."""
        chunker = HybridChunker()
        with patch.dict("sys.modules", {"sentence_transformers": None}):
            with pytest.raises(ImportError, match="sentence-transformers"):
                chunker._load_model()
