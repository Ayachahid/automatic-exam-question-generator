from src.export import (
    ExporterFactory,
    BaseExporter,
    JSONExporter,
    DOCXExporter,
    PDFExporter,
)


def test_imports_from_export_package():
    # Vérifie que les classes sont importables depuis le package export

    assert ExporterFactory is not None
    assert BaseExporter is not None
    assert JSONExporter is not None
    assert DOCXExporter is not None
    assert PDFExporter is not None


def test_export_package_exports_correct_symbols():
    import src.export as export_module

    expected = {
        "ExporterFactory",
        "BaseExporter",
        "JSONExporter",
        "DOCXExporter",
        "PDFExporter",
    }

    # Vérifie que __all__ est bien défini et correct
    assert set(export_module.__all__) == expected
