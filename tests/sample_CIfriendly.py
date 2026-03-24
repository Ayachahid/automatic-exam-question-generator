from src.data.chunkers.semantic import SemanticChunker

def test_chunk_pdf_mock():
    sample_text = "This is a test. It contains multiple sentences. Chunking works!"
    chunker = SemanticChunker(max_sentences=5, min_sentences=2, similarity_threshold=0.6)
    chunks = chunker.chunk(sample_text)
    assert len(chunks) >= 1