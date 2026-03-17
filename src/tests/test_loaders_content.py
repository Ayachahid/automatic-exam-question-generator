import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.data.loaders.registry import LoaderFactory

factory = LoaderFactory()

files = [
    r"src/tests/data_tests/example.txt",
    r"src/tests/data_tests/example.docx",
    r"src/tests/data_tests/example.pdf",
    r"src/tests/data_tests/example.pptx",
    "http://example.com"
]

# Load each file and print first few lines
for f in files:
    loader = factory.get_loader(f)
    text = loader.load(f)
    print(f"\n--- Content of {f} ---\n{text[:500]}")  