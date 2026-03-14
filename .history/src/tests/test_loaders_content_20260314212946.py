from src.data.loaders.registry import LoaderFactory

factory = LoaderFactory()

files = [
    "data_tests\example.txt",
    "data_tests\example.docx",
    "example.pdf",
    #"example.pptx",
    "https://example.com" 
]

# Load each file and print first few lines
for f in files:
    loader = factory.get_loader(f)
    text = loader.load(f)
    print(f"\n--- Content of {f} ---\n{text[:500]}")  