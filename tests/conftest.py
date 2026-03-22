import pytest
import sys
import os
from unittest.mock import MagicMock

# Ensure src is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def sample_text():
    return "This is a sample text for testing purposes. It contains multiple sentences. This is the second sentence. And here is the third one."

@pytest.fixture
def long_sample_text():
    return "Word " * 500  # A long text for chunking tests

@pytest.fixture
def mock_config():
    """Returns a mock configuration object mirroring the structure of src.core.config"""
    config = MagicMock()
    
    # Model Config
    config.model.provider = "ollama"
    config.model.name = "test-model"
    config.model.base_url = "http://localhost:11434"
    
    # Chunker Config
    config.chunker.strategy = "fixed_size"
    config.chunker.chunk_size = 100
    config.chunker.overlap = 20
    
    # Generation Config
    config.generation.question_type = "short_answer"
    config.generation.difficulty = "medium"
    config.generation.num_questions = 2
    
    return config
