import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.data.chunkers.fixed_size import FixedSizeChunker
from src.data.chunkers.sentence import SentenceChunker

def test_chunker(chunker, text, name):
    print(f"\n--- Testing {name} ---")
    chunks = chunker.chunk(text)
    print(f"Total chunks: {len(chunks)}")
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i+1} (length {len(chunk)} characters):")
        # Print only the first 100 characters of each chunk for brevity
        print(f"  {chunk[:100]}...")
    return chunks

def main():
    sample_file = Path("src/tests/data_tests/sample_2000c.txt")
    if not sample_file.exists():
        print(f"Error: Sample file {sample_file} not found.")
        return

    text = sample_file.read_text(encoding="utf-8")
    
    # Test FixedSizeChunker
    fixed_chunker = FixedSizeChunker(chunk_size=500, overlap=50)
    test_chunker(fixed_chunker, text, "FixedSizeChunker")
    
    # Test SentenceChunker
    sentence_chunker = SentenceChunker(max_sentences=5, min_sentences=1)
    test_chunker(sentence_chunker, text, "SentenceChunker")

if __name__ == "__main__":
    main()
