import pytest
from unittest.mock import patch, MagicMock
from src.generation.pipeline import QuestionGenerationPipeline

@pytest.fixture
def mock_load_config(mock_config):
    with patch("src.generation.pipeline.load_config", return_value=mock_config) as mock:
        yield mock

@pytest.fixture
def mock_provider_factory():
    with patch("src.generation.pipeline.ProviderFactory") as mock:
        yield mock

@pytest.fixture
def mock_chunker_factory():
    with patch("src.generation.pipeline.ChunkerFactory") as mock:
        yield mock

@pytest.fixture
def mock_loader_factory():
    with patch("src.generation.pipeline.LoaderFactory") as mock:
        yield mock

def test_pipeline_init(mock_load_config, mock_provider_factory, mock_chunker_factory):
    pipeline = QuestionGenerationPipeline()
    assert pipeline.config is not None
    # Check that provider was requested with correct config
    mock_provider_factory.return_value.get_provider.assert_called()

def test_pipeline_run_text_single_chunk(mock_load_config, mock_provider_factory, mock_chunker_factory, mock_loader_factory):
    # Setup
    mock_provider = MagicMock()
    # Mock LLM Output
    mock_provider.generate.return_value = '''
    ```json
    [
        {"question": "What is Python?", "answer": "A language.", "options": ["A", "B"]}
    ]
    ```
    '''
    mock_provider_factory.return_value.get_provider.return_value = mock_provider
    
    # Mock Chunker: Return 1 chunk
    mock_chunker = MagicMock()
    mock_chunker.chunk.return_value = ["Chunk 1 content"]
    mock_chunker_factory.return_value.get_chunker.return_value = mock_chunker
    
    pipeline = QuestionGenerationPipeline()
    
    # Run
    questions = pipeline.run(text="Sample input", num_questions=1)
    
    assert len(questions) == 1
    assert questions[0]["question"] == "What is Python?"
    
    # Verify flow
    mock_chunker.chunk.assert_called_with(text="Sample input") # Or cleaned text if cleaner is run
    mock_provider.generate.assert_called_once()

def test_pipeline_run_multiple_chunks(mock_load_config, mock_provider_factory, mock_chunker_factory):
    # Setup: 2 chunks, request 2 questions -> 1 per chunk
    mock_provider = MagicMock()
    # Return different Qs for each call if possible, or same (pipeline collects them)
    # Using side_effect to return different responses
    mock_provider.generate.side_effect = [
        '[{"question": "Q1"}]',
        '[{"question": "Q2"}]'
    ]
    mock_provider_factory.return_value.get_provider.return_value = mock_provider
    
    mock_chunker = MagicMock()
    mock_chunker.chunk.return_value = ["Chunk 1", "Chunk 2"]
    mock_chunker_factory.return_value.get_chunker.return_value = mock_chunker
    
    pipeline = QuestionGenerationPipeline()
    
    questions = pipeline.run(text="Long input", num_questions=2)
    
    assert len(questions) == 2
    assert questions[0]["question"] == "Q1"
    assert questions[1]["question"] == "Q2"
    assert mock_provider.generate.call_count == 2
