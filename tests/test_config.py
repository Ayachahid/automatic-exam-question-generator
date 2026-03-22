import pytest
import yaml
import os
from unittest.mock import patch, mock_open
from src.core.config import load_config, AppConfig, ModelConfig, ChunkerConfig, GenerationConfig


class TestConfigDataClasses:
    """Tests for config data classes."""

    def test_model_config(self):
        """Test ModelConfig dataclass."""
        config = ModelConfig(
            provider="ollama",
            name="llama3.2:1b",
            base_url="http://localhost:11434"
        )

        assert config.provider == "ollama"
        assert config.name == "llama3.2:1b"
        assert config.base_url == "http://localhost:11434"

    def test_chunker_config(self):
        """Test ChunkerConfig dataclass."""
        config = ChunkerConfig(
            strategy="fixed_size",
            chunk_size=1000,
            overlap=100
        )

        assert config.strategy == "fixed_size"
        assert config.chunk_size == 1000
        assert config.overlap == 100

    def test_generation_config(self):
        """Test GenerationConfig dataclass."""
        config = GenerationConfig(
            question_type="short_answer",
            difficulty="medium",
            num_questions=5
        )

        assert config.question_type == "short_answer"
        assert config.difficulty == "medium"
        assert config.num_questions == 5

    def test_app_config(self):
        """Test AppConfig dataclass."""
        model_config = ModelConfig("ollama", "llama3", "http://localhost:11434")
        chunker_config = ChunkerConfig("fixed_size", 500, 50)
        generation_config = GenerationConfig("mcq", "easy", 10)

        app_config = AppConfig(
            model=model_config,
            chunker=chunker_config,
            generation=generation_config
        )

        assert app_config.model.provider == "ollama"
        assert app_config.chunker.chunk_size == 500
        assert app_config.generation.num_questions == 10


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_config_default_path(self, tmp_path):
        """Test loading config from default path."""
        config_content = """
model:
  provider: ollama
  name: llama3.2:1b
  base_url: http://localhost:11434

chunker:
  strategy: fixed_size
  chunk_size: 1000
  overlap: 100

generation:
  question_type: short_answer
  difficulty: medium
  num_questions: 3
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)

        # Change to tmp_path to make relative path work
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            config = load_config("config.yaml")

            assert config.model.provider == "ollama"
            assert config.model.name == "llama3.2:1b"
            assert config.chunker.strategy == "fixed_size"
            assert config.chunker.chunk_size == 1000
            assert config.generation.question_type == "short_answer"
            assert config.generation.num_questions == 3
        finally:
            os.chdir(original_cwd)

    def test_load_config_custom_path(self, tmp_path):
        """Test loading config from custom path."""
        config_content = """
model:
  provider: ollama
  name: qwen2.5:3b
  base_url: http://remote:11434

chunker:
  strategy: sentence
  chunk_size: 500
  overlap: 50

generation:
  question_type: multiple_choice
  difficulty: hard
  num_questions: 10
"""
        config_file = tmp_path / "custom_config.yaml"
        config_file.write_text(config_content)

        config = load_config(str(config_file))

        assert config.model.name == "qwen2.5:3b"
        assert config.model.base_url == "http://remote:11434"
        assert config.chunker.strategy == "sentence"
        assert config.generation.difficulty == "hard"

    def test_load_config_file_not_found(self):
        """Test FileNotFoundError for missing config file."""
        with pytest.raises(FileNotFoundError):
            load_config("nonexistent_config.yaml")

    def test_load_config_invalid_yaml(self, tmp_path):
        """Test error for invalid YAML syntax."""
        config_file = tmp_path / "invalid.yaml"
        config_file.write_text("invalid: yaml: content: [")

        with pytest.raises(yaml.YAMLError):
            load_config(str(config_file))

    def test_load_config_missing_model_section(self, tmp_path):
        """Test error for missing model section."""
        config_content = """
chunker:
  strategy: fixed_size
  chunk_size: 1000
  overlap: 100

generation:
  question_type: short_answer
  difficulty: medium
  num_questions: 3
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)

        with pytest.raises(KeyError):
            load_config(str(config_file))

    def test_load_config_missing_chunker_section(self, tmp_path):
        """Test error for missing chunker section."""
        config_content = """
model:
  provider: ollama
  name: llama3
  base_url: http://localhost:11434

generation:
  question_type: short_answer
  difficulty: medium
  num_questions: 3
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)

        with pytest.raises(KeyError):
            load_config(str(config_file))

    def test_load_config_missing_generation_section(self, tmp_path):
        """Test error for missing generation section."""
        config_content = """
model:
  provider: ollama
  name: llama3
  base_url: http://localhost:11434

chunker:
  strategy: fixed_size
  chunk_size: 1000
  overlap: 100
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)

        with pytest.raises(KeyError):
            load_config(str(config_file))

    def test_load_config_alternative_model(self, tmp_path):
        """Test loading config with alternative model settings."""
        config_content = """
model:
  provider: ollama
  name: mistral:7b
  base_url: http://192.168.1.100:11434

chunker:
  strategy: hybrid
  chunk_size: 2000
  overlap: 200

generation:
  question_type: essay
  difficulty: hard
  num_questions: 1
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)

        config = load_config(str(config_file))

        assert config.model.name == "mistral:7b"
        assert config.model.base_url == "http://192.168.1.100:11434"
        assert config.chunker.strategy == "hybrid"
        assert config.generation.question_type == "essay"

    def test_load_config_edge_values(self, tmp_path):
        """Test loading config with edge values."""
        config_content = """
model:
  provider: ollama
  name: tiny-model:100m
  base_url: https://secure-server:443

chunker:
  strategy: fixed_size
  chunk_size: 100
  overlap: 0

generation:
  question_type: true_false
  difficulty: easy
  num_questions: 100
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)

        config = load_config(str(config_file))

        assert config.chunker.overlap == 0
        assert config.generation.num_questions == 100
