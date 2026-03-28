import os
from pathlib import Path
import pytest
from src.export.pdf import PDFExporter
from src.export.pdf import _REPORTLAB_AVAILABLE


@pytest.mark.skipif(not _REPORTLAB_AVAILABLE, reason="reportlab not installed")
def test_pdf_exporter(tmp_path):
    exporter = PDFExporter()

    # Test data
    questions = [
        {
            "question": "What is 2 + 2?",
            "options": ["3", "4", "5", "6"],
            "answer": "B",
            "explanation": "2 + 2 = 4",
            "concepts_tested": ["math", "arithmetic"],
        },
        {
            "question": "Explain OOP",
            "scenario": "Class Animal is extended by Dog",
            "answer": "Inheritance allows reuse",
            "concepts_tested": ["OOP", "inheritance"],
        },
    ]

    output_file = tmp_path / "output.pdf"

    # Act
    result_path = exporter.export(questions, str(output_file))

    # Assert
    assert Path(result_path).exists()
    assert result_path.endswith(".pdf")
    assert os.path.getsize(result_path) > 0
