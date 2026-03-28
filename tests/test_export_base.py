import pytest
from abc import ABC, abstractmethod


class BaseExporter(ABC):

    @abstractmethod
    def export(self, questions: list[dict], output_path: str) -> str:
        raise NotImplementedError


class DummyExporter(BaseExporter):
    def export(self, _: list[dict], output_path: str) -> str:
        return output_path


class FailingExporter(BaseExporter):
    def export(self, _: list[dict], __: str) -> str:
        raise Exception("Export failed")


def test_cannot_instantiate_base_exporter():
    """La classe abstraite ne doit pas être instanciable"""
    with pytest.raises(TypeError):
        BaseExporter()


def test_export_returns_output_path(tmp_path):
    """Test du cas normal"""
    exporter = DummyExporter()

    questions = [{"question": "What is Python?", "answer": "A programming language"}]

    output_file = tmp_path / "output.txt"

    result = exporter.export(questions, str(output_file))

    assert result == str(output_file)


def test_export_with_empty_list(tmp_path):
    """Test avec liste vide"""
    exporter = DummyExporter()

    output_file = tmp_path / "empty.txt"

    result = exporter.export([], str(output_file))

    assert result == str(output_file)


def test_export_failure():
    """Test du cas d'erreur"""
    exporter = FailingExporter()

    with pytest.raises(Exception, match="Export failed"):
        exporter.export([], "file.txt")
