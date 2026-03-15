import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.data.loaders.registry import LoaderFactory
def test_loader_factory():
    factory = LoaderFactory()

    # TXT
    txt_loader = factory.get_loader("example.txt")
    print("TXT loader:", type(txt_loader))

    # DOCX
    docx_loader = factory.get_loader("example.docx")
    print("DOCX loader:", type(docx_loader))

    # PDF
    pdf_loader = factory.get_loader("example.pdf")
    print("PDF loader:", type(pdf_loader))

    # Web
    web_loader = factory.get_loader("http://example.com")
    print("Web loader:", type(web_loader))

    #pptx

if __name__ == "__main__":
    test_loader_factory()