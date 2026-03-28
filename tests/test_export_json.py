import json
from src.export.json import JSONExporter


def test_json_export_creates_file(tmp_path):
    """Vérifie que le fichier JSON est créé"""
    exporter = JSONExporter()

    questions = [
        {"question": "Q1", "answer": "A1"},
        {"question": "Q2", "answer": "A2"},
    ]

    output_file = tmp_path / "test.json"

    result = exporter.export(questions, str(output_file))

    # fichier existe
    assert output_file.exists()

    # chemin retourné est correct
    assert result == str(output_file.absolute())


def test_json_export_content_structure(tmp_path):
    """Vérifie la structure du JSON"""
    exporter = JSONExporter()

    questions = [
        {"question": "What is Python?", "answer": "A language"},
    ]

    output_file = tmp_path / "output.json"

    exporter.export(questions, str(output_file))

    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "total" in data
    assert "questions" in data

    assert data["total"] == 1
    assert data["questions"] == questions


def test_json_export_empty_questions(tmp_path):
    """Test avec liste vide"""
    exporter = JSONExporter()

    output_file = tmp_path / "empty.json"

    exporter.export([], str(output_file))

    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["total"] == 0
    assert data["questions"] == []


def test_json_export_preserves_optional_fields(tmp_path):
    """Vérifie que les champs optionnels sont gardés"""
    exporter = JSONExporter()

    questions = [
        {
            "question": "What is 2+2?",
            "answer": "4",
            "options": ["1", "2", "3", "4"],
            "explanation": "Basic math",
        }
    ]

    output_file = tmp_path / "full.json"

    exporter.export(questions, str(output_file))

    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    q = data["questions"][0]

    assert q["options"] == ["1", "2", "3", "4"]
    assert q["explanation"] == "Basic math"


def test_json_export_creates_directories(tmp_path):
    """Vérifie que les dossiers sont créés automatiquement"""
    exporter = JSONExporter()

    nested_path = tmp_path / "a" / "b" / "c" / "file.json"

    exporter.export([], str(nested_path))

    assert nested_path.exists()
