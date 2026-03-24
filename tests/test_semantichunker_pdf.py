# import fitz  # PyMuPDF
# from src.data.chunkers.semantic import SemanticChunker

# pdf_path = "tests/data/child-abuse.pdf"


# text = ""
# (doc = fitz.open(pdf_path)
# for page in doc:
# page_text = page.get_text()
# if page_text:
# text += page_text + "\n"
# doc.close()

# chunker = SemanticChunker(max_sentences=5, min_sentences=2, similarity_threshold=0.6)

# chunks = chunker.chunk(text)


# for i, chunk in enumerate(chunks, 1):
#    print(f"--- Chunk {i} ---")
#    print(chunk)
#    print()
