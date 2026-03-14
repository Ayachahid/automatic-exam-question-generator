from loaders.registry import LoaderFactory

def test_loader_factory():
    factory = LoaderFactory()

    # TXT
    txt_loader = factory.get_loader("c")
    print("TXT loader:", type(txt_loader))

    # DOCX
    docx_loader = factory.get_loader("example.docx")
    print("DOCX loader:", type(docx_loader))

    # PDF
    pdf_loader = factory.get_loader("example.pdf")
    print("PDF loader:", type(pdf_loader))

    # PPTX
    pptx_loader = factory.get_loader("example.pptx")
    print("PPTX loader:", type(pptx_loader))

    # Web
    web_loader = factory.get_loader("https://example.com")
    print("Web loader:", type(web_loader))

if __name__ == "__main__":
    test_loader_factory()