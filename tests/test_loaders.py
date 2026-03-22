import pytest
from unittest.mock import patch, MagicMock
from src.data.loaders.registry import LoaderFactory
from src.data.loaders.txt import TXTLoader
from src.data.loaders.pdf import PDFLoader
from src.data.loaders.docx import DOCXLoader
from src.core.exceptions import UnsupportedFormatError

def test_loader_factory_types():
    factory = LoaderFactory()
    assert isinstance(factory.get_loader("test.txt"), TXTLoader)
    assert isinstance(factory.get_loader("test.pdf"), PDFLoader)
    assert isinstance(factory.get_loader("test.docx"), DOCXLoader)
    
def test_loader_factory_unknown():
    factory = LoaderFactory()
    with pytest.raises(UnsupportedFormatError):
        factory.get_loader("test.unknown")

def test_txt_loader_real_file(tmp_path):
    # Use pytest's tmp_path fixture for real file testing
    d = tmp_path / "subdir"
    d.mkdir()
    p = d / "hello.txt"
    p.write_text("Hello World", encoding="utf-8")
    
    loader = TXTLoader()
    content = loader.load(str(p))
    assert content == "Hello World"

@patch("src.data.loaders.pdf.fitz") 
def test_pdf_loader_mock(mock_fitz):
    # Mock the document object
    mock_doc = MagicMock()
    # Mock context manager behavior if used as 'with fitz.open() as doc:'
    mock_doc.__enter__.return_value = mock_doc
    mock_doc.__exit__.return_value = None
    
    mock_page = MagicMock()
    mock_page.get_text.return_value = "PDF Content"
    mock_doc.__iter__.return_value = [mock_page]
    
    mock_fitz.open.return_value = mock_doc
    
    loader = PDFLoader()
    content = loader.load("dummy.pdf")
    
    mock_fitz.open.assert_called_with("dummy.pdf")
    assert "PDF Content" in content

@patch("src.data.loaders.docx.Document")
def test_docx_loader_mock(mock_document_cls):
    # Mock the Document instance
    mock_doc = MagicMock()
    mock_para = MagicMock()
    mock_para.text = "DOCX Content"
    mock_doc.paragraphs = [mock_para]
    mock_document_cls.return_value = mock_doc
    
    loader = DOCXLoader()
    content = loader.load("dummy.docx")
    
    mock_document_cls.assert_called_with("dummy.docx")
    assert "DOCX Content" in content
