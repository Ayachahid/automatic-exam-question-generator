import pytest
from src.export.registry import ExporterFactory
from src.export.json import JSONExporter
from src.export.docx import DOCXExporter
from src.export.pdf import PDFExporter


def test_supported_formats():
    formats = ExporterFactory.supported_formats()

    assert "json" in formats
    assert "docx" in formats
    assert "pdf" in formats
    assert len(formats) == 3


def test_factory_returns_json_exporter():
    factory = ExporterFactory()

    exporter = factory.get_exporter("json")

    assert isinstance(exporter, JSONExporter)


def test_factory_returns_docx_exporter():
    factory = ExporterFactory()

    exporter = factory.get_exporter("docx")

    assert isinstance(exporter, DOCXExporter)


def test_factory_returns_pdf_exporter():
    factory = ExporterFactory()

    exporter = factory.get_exporter("pdf")

    assert isinstance(exporter, PDFExporter)


def test_factory_accepts_case_and_spaces():
    factory = ExporterFactory()

    exporter = factory.get_exporter("  JSON  ")

    assert isinstance(exporter, JSONExporter)


def test_factory_invalid_format_raises():
    factory = ExporterFactory()

    with pytest.raises(ValueError) as exc_info:
        factory.get_exporter("xml")

    assert "Unsupported export format" in str(exc_info.value)
