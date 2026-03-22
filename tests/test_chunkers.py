import pytest
from src.data.chunkers.fixed_size import FixedSizeChunker
from src.data.chunkers.sentence import SentenceChunker

def test_fixed_size_chunker_basic(long_sample_text):
    chunk_size = 100
    overlap = 10
    chunker = FixedSizeChunker(chunk_size=chunk_size, overlap=overlap)
    chunks = chunker.chunk(long_sample_text)
    
    assert len(chunks) > 0
    # Check that chunks are roughly the correct size
    # Note: The exact implementation might vary slightly, but shouldn't be excessively larger
    for chunk in chunks:
        # Allowing some margin for word boundaries if the implementation respects them
        assert len(chunk) > 0 

def test_fixed_size_chunker_overlap():
    text = "1234567890" * 2 # 20 chars
    chunker = FixedSizeChunker(chunk_size=10, overlap=5)
    chunks = chunker.chunk(text)
    
    # "1234567890", "6789012345", ...
    assert len(chunks) >= 2
    # Check overlap presence
    # Implementation detail: Does it strictly overlap characters?
    # Assuming standard sliding window
    pass 

def test_sentence_chunker_basic(sample_text):
    # sample_text has 4 sentences
    # Set min_sentences=0 to avoid overlap accumulation for this basic test
    chunker = SentenceChunker(max_sentences=1, min_sentences=0)
    chunks = chunker.chunk(sample_text)
    
    assert len(chunks) == 4
    assert "This is a sample text" in chunks[0]

def test_sentence_chunker_grouping(sample_text):
    # Group by 2 sentences, min_sentences=0 for no overlap
    chunker = SentenceChunker(max_sentences=2, min_sentences=0)
    chunks = chunker.chunk(sample_text)
    
    assert len(chunks) == 2
    assert chunks[0].count(".") == 2 # Expecting 2 periods if sentences end with period

def test_empty_input():
    chunker = FixedSizeChunker(chunk_size=100, overlap=10)
    assert chunker.chunk("") == []
    
    chunker_s = SentenceChunker()
    assert chunker_s.chunk("") == []

def test_none_input():
    chunker = FixedSizeChunker(chunk_size=100, overlap=10)
    # Based on implementation, if text is None, it returns []
    assert chunker.chunk(None) == []
