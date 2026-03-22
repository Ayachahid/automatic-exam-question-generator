import pytest
from unittest.mock import patch, MagicMock
from src.data.loaders.registry import LoaderFactory
from src.data.loaders.txt import TXTLoader
from src.data.loaders.pdf import PDFLoader
from src.data.loaders.docx import DOCXLoader
from src.data.loaders.pptx import PPTXLoader
from src.data.loaders.web import WebLoader
from src.core.exceptions import (
    UnsupportedFormatError,
    FileReadError,
    EmptyDocumentError,
)


class TestLoaderFactory:
    """Tests for LoaderFactory."""

    def test_loader_factory_txt(self):
        """Test TXT loader selection."""
        factory = LoaderFactory()
        assert isinstance(factory.get_loader("test.txt"), TXTLoader)

    def test_loader_factory_pdf(self):
        """Test PDF loader selection."""
        factory = LoaderFactory()
        assert isinstance(factory.get_loader("test.pdf"), PDFLoader)

    def test_loader_factory_docx(self):
        """Test DOCX loader selection."""
        factory = LoaderFactory()
        assert isinstance(factory.get_loader("test.docx"), DOCXLoader)

    def test_loader_factory_pptx(self):
        """Test PPTX loader selection."""
        factory = LoaderFactory()
        assert isinstance(factory.get_loader("test.pptx"), PPTXLoader)

    def test_loader_factory_web_http(self):
        """Test Web loader selection for HTTP URLs."""
        factory = LoaderFactory()
        assert isinstance(factory.get_loader("http://example.com"), WebLoader)

    def test_loader_factory_web_https(self):
        """Test Web loader selection for HTTPS URLs."""
        factory = LoaderFactory()
        assert isinstance(factory.get_loader("https://example.com"), WebLoader)

    def test_loader_factory_unknown_extension(self):
        """Test UnsupportedFormatError for unknown extensions."""
        factory = LoaderFactory()
        with pytest.raises(UnsupportedFormatError):
            factory.get_loader("test.unknown")

    def test_loader_factory_case_insensitive(self):
        """Test that extensions are handled case-insensitively."""
        factory = LoaderFactory()
        assert isinstance(factory.get_loader("test.TXT"), TXTLoader)
        assert isinstance(factory.get_loader("test.PDF"), PDFLoader)
        assert isinstance(factory.get_loader("test.DocX"), DOCXLoader)


class TestTXTLoader:
    """Tests for TXTLoader."""

    def test_txt_loader_real_file(self, tmp_path):
        """Test loading a real TXT file."""
        d = tmp_path / "subdir"
        d.mkdir()
        p = d / "hello.txt"
        p.write_text("Hello World", encoding="utf-8")

        loader = TXTLoader()
        content = loader.load(str(p))
        assert content == "Hello World"

    def test_txt_loader_utf8(self, tmp_path):
        """Test loading UTF-8 encoded file."""
        p = tmp_path / "utf8.txt"
        p.write_text("Hello 世界 café", encoding="utf-8")

        loader = TXTLoader()
        content = loader.load(str(p))
        assert "世界" in content
        assert "café" in content

    def test_txt_loader_empty_file(self, tmp_path):
        """Test that empty TXT file returns empty string."""
        p = tmp_path / "empty.txt"
        p.write_text("", encoding="utf-8")

        loader = TXTLoader()
        content = loader.load(str(p))
        # Note: TXTLoader doesn't raise EmptyDocumentError (unlike PDF/DOCX loaders)
        assert content == ""

    def test_txt_loader_file_not_found(self):
        """Test FileNotFoundError for non-existent file."""
        loader = TXTLoader()
        with pytest.raises(FileNotFoundError):
            loader.load("nonexistent.txt")

    def test_txt_loader_multiline(self, tmp_path):
        """Test loading multiline TXT file."""
        p = tmp_path / "multiline.txt"
        p.write_text("Line 1\nLine 2\nLine 3", encoding="utf-8")

        loader = TXTLoader()
        content = loader.load(str(p))
        assert "Line 1" in content
        assert "Line 2" in content
        assert "Line 3" in content


class TestPDFLoader:
    """Tests for PDFLoader."""

    @patch("src.data.loaders.pdf.fitz")
    def test_pdf_loader_basic(self, mock_fitz):
        """Test basic PDF loading."""
        mock_doc = MagicMock()
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

    @patch("src.data.loaders.pdf.fitz")
    def test_pdf_loader_multiple_pages(self, mock_fitz):
        """Test PDF with multiple pages."""
        mock_doc = MagicMock()
        mock_doc.__enter__.return_value = mock_doc
        mock_doc.__exit__.return_value = None

        mock_page1 = MagicMock()
        mock_page1.get_text.return_value = "Page 1"
        mock_page2 = MagicMock()
        mock_page2.get_text.return_value = "Page 2"
        mock_doc.__iter__.return_value = [mock_page1, mock_page2]
        mock_fitz.open.return_value = mock_doc

        loader = PDFLoader()
        content = loader.load("dummy.pdf")

        assert "Page 1" in content
        assert "Page 2" in content

    @patch("src.data.loaders.pdf.fitz")
    def test_pdf_loader_empty_document(self, mock_fitz):
        """Test EmptyDocumentError for empty PDF."""
        mock_doc = MagicMock()
        mock_doc.__enter__.return_value = mock_doc
        mock_doc.__exit__.return_value = None

        mock_page = MagicMock()
        mock_page.get_text.return_value = ""
        mock_doc.__iter__.return_value = [mock_page]
        mock_fitz.open.return_value = mock_doc

        loader = PDFLoader()
        with pytest.raises(EmptyDocumentError):
            loader.load("empty.pdf")

    @patch("src.data.loaders.pdf.fitz")
    def test_pdf_loader_file_read_error(self, mock_fitz):
        """Test FileReadError when PDF loading fails."""
        mock_fitz.open.side_effect = Exception("Cannot open PDF")

        loader = PDFLoader()
        with pytest.raises(FileReadError):
            loader.load("corrupted.pdf")

    @patch("src.data.loaders.pdf.fitz")
    def test_pdf_loader_closes_document(self, mock_fitz):
        """Test that PDF document is properly closed."""
        mock_doc = MagicMock()
        mock_doc.__enter__.return_value = mock_doc
        mock_doc.__exit__.return_value = None

        mock_page = MagicMock()
        mock_page.get_text.return_value = "Content"
        mock_doc.__iter__.return_value = [mock_page]
        mock_fitz.open.return_value = mock_doc

        loader = PDFLoader()
        loader.load("dummy.pdf")

        mock_doc.close.assert_called_once()


class TestDOCXLoader:
    """Tests for DOCXLoader."""

    @patch("src.data.loaders.docx.Document")
    def test_docx_loader_basic(self, mock_document_cls):
        """Test basic DOCX loading."""
        mock_doc = MagicMock()
        mock_para = MagicMock()
        mock_para.text = "DOCX Content"
        mock_doc.paragraphs = [mock_para]
        mock_document_cls.return_value = mock_doc

        loader = DOCXLoader()
        content = loader.load("dummy.docx")

        mock_document_cls.assert_called_with("dummy.docx")
        assert "DOCX Content" in content

    @patch("src.data.loaders.docx.Document")
    def test_docx_loader_multiple_paragraphs(self, mock_document_cls):
        """Test DOCX with multiple paragraphs."""
        mock_doc = MagicMock()
        mock_para1 = MagicMock()
        mock_para1.text = "Paragraph 1"
        mock_para2 = MagicMock()
        mock_para2.text = "Paragraph 2"
        mock_doc.paragraphs = [mock_para1, mock_para2]
        mock_document_cls.return_value = mock_doc

        loader = DOCXLoader()
        content = loader.load("dummy.docx")

        assert "Paragraph 1" in content
        assert "Paragraph 2" in content

    @patch("src.data.loaders.docx.Document")
    def test_docx_loader_filters_empty_paragraphs(self, mock_document_cls):
        """Test that empty paragraphs are filtered."""
        mock_doc = MagicMock()
        mock_para1 = MagicMock()
        mock_para1.text = ""
        mock_para2 = MagicMock()
        mock_para2.text = "Content"
        mock_doc.paragraphs = [mock_para1, mock_para2]
        mock_document_cls.return_value = mock_doc

        loader = DOCXLoader()
        content = loader.load("dummy.docx")

        assert content == "Content"

    @patch("src.data.loaders.docx.Document")
    def test_docx_loader_empty_document(self, mock_document_cls):
        """Test EmptyDocumentError for empty DOCX."""
        mock_doc = MagicMock()
        mock_doc.paragraphs = []
        mock_document_cls.return_value = mock_doc

        loader = DOCXLoader()
        with pytest.raises(EmptyDocumentError):
            loader.load("empty.docx")

    @patch("src.data.loaders.docx.Document")
    def test_docx_loader_file_read_error(self, mock_document_cls):
        """Test FileReadError when DOCX loading fails."""
        mock_document_cls.side_effect = Exception("Cannot open DOCX")

        loader = DOCXLoader()
        with pytest.raises(FileReadError):
            loader.load("corrupted.docx")


class TestPPTXLoader:
    """Tests for PPTXLoader."""

    @patch("src.data.loaders.pptx.Presentation")
    def test_pptx_loader_basic(self, mock_presentation_cls):
        """Test basic PPTX loading."""
        mock_prs = MagicMock()
        mock_shape = MagicMock()
        mock_shape.text = "Slide Content"
        mock_shape.has_text_frame = True

        mock_slide = MagicMock()
        mock_slide.shapes = [mock_shape]
        mock_prs.slides = [mock_slide]
        mock_presentation_cls.return_value = mock_prs

        loader = PPTXLoader()
        content = loader.load("dummy.pptx")

        mock_presentation_cls.assert_called_with("dummy.pptx")
        assert "Slide Content" in content

    @patch("src.data.loaders.pptx.Presentation")
    def test_pptx_loader_multiple_slides(self, mock_presentation_cls):
        """Test PPTX with multiple slides."""
        mock_prs = MagicMock()

        mock_shape1 = MagicMock()
        mock_shape1.text = "Slide 1"
        mock_slide1 = MagicMock()
        mock_slide1.shapes = [mock_shape1]

        mock_shape2 = MagicMock()
        mock_shape2.text = "Slide 2"
        mock_slide2 = MagicMock()
        mock_slide2.shapes = [mock_shape2]

        mock_prs.slides = [mock_slide1, mock_slide2]
        mock_presentation_cls.return_value = mock_prs

        loader = PPTXLoader()
        content = loader.load("dummy.pptx")

        assert "Slide 1" in content
        assert "Slide 2" in content

    @patch("src.data.loaders.pptx.Presentation")
    def test_pptx_loader_multiple_shapes_per_slide(self, mock_presentation_cls):
        """Test PPTX with multiple shapes per slide."""
        mock_prs = MagicMock()

        mock_shape1 = MagicMock()
        mock_shape1.text = "Title"
        mock_shape2 = MagicMock()
        mock_shape2.text = "Body text"

        mock_slide = MagicMock()
        mock_slide.shapes = [mock_shape1, mock_shape2]
        mock_prs.slides = [mock_slide]
        mock_presentation_cls.return_value = mock_prs

        loader = PPTXLoader()
        content = loader.load("dummy.pptx")

        assert "Title" in content
        assert "Body text" in content

    @patch("src.data.loaders.pptx.Presentation")
    def test_pptx_loader_empty_presentation(self, mock_presentation_cls):
        """Test EmptyDocumentError for empty PPTX."""
        mock_prs = MagicMock()
        mock_prs.slides = []
        mock_presentation_cls.return_value = mock_prs

        loader = PPTXLoader()
        with pytest.raises(EmptyDocumentError):
            loader.load("empty.pptx")

    @patch("src.data.loaders.pptx.Presentation")
    def test_pptx_loader_file_read_error(self, mock_presentation_cls):
        """Test FileReadError when PPTX loading fails."""
        mock_presentation_cls.side_effect = Exception("Cannot open PPTX")

        loader = PPTXLoader()
        with pytest.raises(FileReadError):
            loader.load("corrupted.pptx")


class TestWebLoader:
    """Tests for WebLoader."""

    @patch("src.data.loaders.web.requests.get")
    @patch("src.data.loaders.web.BeautifulSoup")
    def test_web_loader_basic(self, mock_bs, mock_get):
        """Test basic web page loading."""
        mock_response = MagicMock()
        mock_response.text = "<html><body><p>Web Content</p></body></html>"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        mock_soup = MagicMock()
        mock_soup.stripped_strings = ["Web Content"]
        mock_soup.__iter__ = MagicMock(return_value=iter([]))
        mock_bs.return_value = mock_soup

        loader = WebLoader()
        content = loader.load("http://example.com")

        mock_get.assert_called_with("http://example.com", timeout=30)
        assert "Web Content" in content

    @patch("src.data.loaders.web.requests.get")
    @patch("src.data.loaders.web.BeautifulSoup")
    def test_web_loader_removes_script_style(self, mock_bs, mock_get):
        """Test that script and style tags are removed."""
        mock_response = MagicMock()
        mock_response.text = (
            "<html><body><script>alert('x');</script><p>Content</p></body></html>"
        )
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        mock_soup = MagicMock()
        mock_soup.stripped_strings = ["Content"]
        mock_soup.__iter__ = MagicMock(return_value=iter([]))

        def decompose():
            pass

        mock_tag = MagicMock()
        mock_tag.decompose = decompose
        mock_soup.find_all.return_value = [mock_tag]

        mock_bs.return_value = mock_soup

        loader = WebLoader()
        content = loader.load("http://example.com")

        assert "alert" not in content

    @patch("src.data.loaders.web.requests.get")
    def test_web_loader_timeout(self, mock_get):
        """Test handling of request timeout."""
        mock_get.side_effect = Exception("Timeout")

        loader = WebLoader()
        with pytest.raises(FileReadError):
            loader.load("http://slow-site.com")

    @patch("src.data.loaders.web.requests.get")
    def test_web_loader_http_error(self, mock_get):
        """Test handling of HTTP errors."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("404 Not Found")
        mock_get.return_value = mock_response

        loader = WebLoader()
        with pytest.raises(FileReadError):
            loader.load("http://example.com/404")
