from src.data.loaders.registry import LoaderFactory

factory = LoaderFactory()

files = [
    r"data_tests/example.txt",
    r"data_tests/example.docx",
    r"data_tests/example.pdf",
    r"data_tests/example.pptx",  his file
    "https://example.com"
]

# Load each file and print first few lines
for f in files:
    loader = factory.get_loader(f)
    text = loader.load(f)
    print(f"\n--- Content of {f} ---\n{text[:500]}")  