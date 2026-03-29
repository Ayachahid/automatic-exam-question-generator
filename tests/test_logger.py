import logging
import pytest
from io import StringIO
from docx import Document
from unittest.mock import patch, Mock

from src.data.loaders.docx import DOCXLoader
from src.data.chunkers.fixed_size import FixedSizeChunker
from src.data.chunkers.registry import ChunkerFactory
from src.export.registry import ExporterFactory
from src.providers.registry import ProviderFactory
from src.providers.ollama import OllamaProvider
from src.core.config import load_config


@pytest.fixture
def log_capture():
    buf = StringIO()
    handler = logging.StreamHandler(buf)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter("%(message)s"))

    exam_logger = logging.getLogger("exam_generator")
    original_level = exam_logger.level
    exam_logger.setLevel(logging.DEBUG)
    exam_logger.addHandler(handler)

    yield buf

    exam_logger.removeHandler(handler)
    exam_logger.setLevel(original_level)


def get_logs(buf: StringIO) -> str:
    return buf.getvalue().lower()


def test_docx_loader_logger(log_capture, tmp_path):
    file_path = tmp_path / "test.docx"
    doc = Document()
    doc.add_paragraph("Hello world")
    doc.save(file_path)

    loader = DOCXLoader()
    loader.load(str(file_path))

    logs = get_logs(log_capture)

    assert "loading docx file" in logs
    assert "successfully loaded docx file" in logs


def test_config_logger(log_capture, tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("""
model:
  provider: ollama
  name: qwen2.5:3b
  base_url: http://localhost:11434

chunker:
  strategy: fixed_size
  chunk_size: 100
  overlap: 10
  model_name: null
  similarity_threshold: 0.5
  max_sentences: 5
  min_sentences: 1
  batch_size: 1

generation:
  question_type: multiple_choice
  difficulty: easy
  num_questions: 5
""")

    load_config(str(config_file))

    logs = get_logs(log_capture)

    assert "loading config from" in logs
    assert "config loaded" in logs


def test_fixed_chunker_logger(log_capture):
    chunker = FixedSizeChunker(chunk_size=50, overlap=5)
    chunker.chunk("This is a test text for chunking purposes.")

    logs = get_logs(log_capture)

    # DEBUG : "FixedSizeChunker initialized: chunk_size=50 overlap=5"
    assert "fixedsize" in logs or "initialized" in logs
    # DEBUG : "FixedSizeChunker produced N chunks"
    assert "produced" in logs or "chunks" in logs


def test_chunker_factory_logger(log_capture):
    factory = ChunkerFactory()
    factory.get_chunker("fixed_size")

    logs = get_logs(log_capture)

    assert "requested chunker" in logs
    assert "using fixedsize" in logs or "fixedsize" in logs


def test_exporter_factory_logger(log_capture):
    factory = ExporterFactory()
    factory.get_exporter("json")

    logs = get_logs(log_capture)

    assert "requested exporter format" in logs
    assert "exporter instantiated successfully" in logs


def test_provider_factory_logger(log_capture):
    factory = ProviderFactory()
    factory.get_provider(
        provider_name="ollama",
        base_url="http://localhost:11434",
        model="llama3",
    )

    logs = get_logs(log_capture)

    assert "selecting provider" in logs
    assert "ollamaprovider initialized" in logs


@patch("src.providers.ollama.httpx.post")
def test_ollama_provider_logger(mock_post, log_capture):
    mock_response = Mock()
    mock_response.json.return_value = {"response": "hello"}
    mock_post.return_value = mock_response

    provider = OllamaProvider(
        base_url="http://localhost:11434",
        model="llama3",
    )
    provider.generate("test prompt")

    logs = get_logs(log_capture)

    assert "ollamaprovider initialized" in logs
    assert "sending request to ollama api" in logs
