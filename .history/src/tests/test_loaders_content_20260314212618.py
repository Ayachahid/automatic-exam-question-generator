from src.data.loaders.registry import LoaderFactory

# Create the factory
factory = LoaderFactory()

# Your test files
files = [
    "example.txt",
    "example.docx",
    "example.pdf",
    "example.pptx",
    "https://example.com"  # WebLoader
]

# Load each file and print first few lines
for f in files:
    loader = factory.get_loader(f)
    text = loader.load(f)
    print(f"\n--- Content of {f} ---\n{text[:500]}")  # first 500 chars