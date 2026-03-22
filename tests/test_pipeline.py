import pytest
from unittest.mock import patch, MagicMock
from src.generation.pipeline import QuestionGenerationPipeline
from src.core.exceptions import EmptyDocumentError


@pytest.fixture
def mock_load_config(mock_config):
    """Mock config loading."""
    with patch("src.generation.pipeline.load_config", return_value=mock_config) as mock:
        yield mock


@pytest.fixture
def mock_provider_factory():
    """Mock ProviderFactory."""
    with patch("src.generation.pipeline.ProviderFactory") as mock:
        yield mock


@pytest.fixture
def mock_chunker_factory():
    """Mock ChunkerFactory."""
    with patch("src.generation.pipeline.ChunkerFactory") as mock:
        yield mock


@pytest.fixture
def mock_loader_factory():
    """Mock LoaderFactory."""
    with patch("src.generation.pipeline.LoaderFactory") as mock:
        yield mock


class TestPipelineInitialization:
    """Tests for pipeline initialization."""

    def test_pipeline_init(self, mock_load_config, mock_provider_factory, mock_chunker_factory):
        """Test basic pipeline initialization."""
        pipeline = QuestionGenerationPipeline()
        assert pipeline.config is not None
        mock_provider_factory.return_value.get_provider.assert_called()

    def test_pipeline_init_with_custom_config_path(self, mock_load_config, mock_provider_factory):
        """Test initialization with custom config path."""
        pipeline = QuestionGenerationPipeline(config_path="custom/config.yaml")
        mock_load_config.assert_called_with("custom/config.yaml")

    def test_pipeline_init_with_file_path(self, mock_load_config, mock_provider_factory):
        """Test initialization with file path."""
        pipeline = QuestionGenerationPipeline(file_path="test.pdf")
        assert pipeline.file_path == "test.pdf"

    def test_pipeline_components_initialized(self, mock_load_config, mock_provider_factory, mock_chunker_factory, mock_loader_factory):
        """Test that all pipeline components are initialized."""
        pipeline = QuestionGenerationPipeline()

        assert pipeline.loader is not None
        assert pipeline.cleaner is not None
        assert pipeline.chunker is not None
        assert pipeline.prompter is not None
        assert pipeline.parser is not None
        assert pipeline.provider is not None


class TestPipelineRunText:
    """Tests for pipeline run with text input."""

    def test_pipeline_run_text_single_chunk(self, mock_load_config, mock_provider_factory, mock_chunker_factory):
        """Test running pipeline with single chunk."""
        mock_provider = MagicMock()
        mock_provider.generate.return_value = '''
        ```json
        [{"question": "What is Python?", "answer": "A language.", "options": ["A", "B"]}]
        ```
        '''
        mock_provider_factory.return_value.get_provider.return_value = mock_provider

        mock_chunker = MagicMock()
        mock_chunker.chunk.return_value = ["Chunk 1 content"]
        mock_chunker_factory.return_value.get_chunker.return_value = mock_chunker

        pipeline = QuestionGenerationPipeline()
        questions = pipeline.run(text="Sample input", num_questions=1)

        assert len(questions) == 1
        assert questions[0]["question"] == "What is Python?"

    def test_pipeline_run_text_multiple_chunks(self, mock_load_config, mock_provider_factory, mock_chunker_factory):
        """Test running pipeline with multiple chunks."""
        mock_provider = MagicMock()
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

    def test_pipeline_run_text_cleans_input(self, mock_load_config, mock_provider_factory, mock_chunker_factory):
        """Test that text is cleaned before chunking."""
        mock_provider = MagicMock()
        mock_provider.generate.return_value = '[]'
        mock_provider_factory.return_value.get_provider.return_value = mock_provider

        mock_chunker = MagicMock()
        mock_chunker.chunk.return_value = ["cleaned chunk"]
        mock_chunker_factory.return_value.get_chunker.return_value = mock_chunker

        pipeline = QuestionGenerationPipeline()
        pipeline.run(text="  Dirty  text  ", num_questions=1)

        # Verify cleaner was called (chunker receives cleaned text)
        mock_chunker.chunk.assert_called()
        call_args = mock_chunker.chunk.call_args[1]
        assert "Dirty" in call_args["text"]

    def test_pipeline_run_text_no_questions_requested(self, mock_load_config, mock_provider_factory, mock_chunker_factory):
        """Test running pipeline with zero questions."""
        mock_provider = MagicMock()
        mock_provider_factory.return_value.get_provider.return_value = mock_provider

        mock_chunker = MagicMock()
        mock_chunker.chunk.return_value = ["Chunk"]
        mock_chunker_factory.return_value.get_chunker.return_value = mock_chunker

        pipeline = QuestionGenerationPipeline()
        questions = pipeline.run(text="Input", num_questions=0)

        assert len(questions) == 0

    def test_pipeline_run_text_more_requested_than_chunks(self, mock_load_config, mock_provider_factory, mock_chunker_factory):
        """Test requesting more questions than chunks."""
        mock_provider = MagicMock()
        mock_provider.generate.return_value = '[{"question": "Q1"}, {"question": "Q2"}, {"question": "Q3"}]'
        mock_provider_factory.return_value.get_provider.return_value = mock_provider

        mock_chunker = MagicMock()
        mock_chunker.chunk.return_value = ["Chunk 1"]  # Only 1 chunk
        mock_chunker_factory.return_value.get_chunker.return_value = mock_chunker

        pipeline = QuestionGenerationPipeline()
        questions = pipeline.run(text="Input", num_questions=5)

        # Should get up to 3 questions from single chunk
        assert len(questions) <= 3

    def test_pipeline_run_text_early_stop(self, mock_load_config, mock_provider_factory, mock_chunker_factory):
        """Test that pipeline stops early when enough questions generated."""
        mock_provider = MagicMock()
        # Each chunk returns 5 questions, but we only need 3
        mock_provider.generate.return_value = '[{"q": "1"}, {"q": "2"}, {"q": "3"}, {"q": "4"}, {"q": "5"}]'
        mock_provider_factory.return_value.get_provider.return_value = mock_provider

        mock_chunker = MagicMock()
        mock_chunker.chunk.return_value = ["Chunk 1", "Chunk 2", "Chunk 3"]
        mock_chunker_factory.return_value.get_chunker.return_value = mock_chunker

        pipeline = QuestionGenerationPipeline()
        questions = pipeline.run(text="Input", num_questions=3)

        assert len(questions) == 3
        # Should only call generate once (first chunk provides enough)
        assert mock_provider.generate.call_count == 1

    def test_pipeline_run_text_no_input_source(self, mock_load_config):
        """Test ValueError when no input source provided."""
        pipeline = QuestionGenerationPipeline()

        with pytest.raises(ValueError) as exc_info:
            pipeline.run()

        assert "No input source" in str(exc_info.value)


class TestPipelineRunFile:
    """Tests for pipeline run with file input."""

    def test_pipeline_run_file(self, mock_load_config, mock_provider_factory, mock_chunker_factory, mock_loader_factory):
        """Test running pipeline with file input."""
        mock_loader = MagicMock()
        mock_loader.load.return_value = "File content"
        mock_loader_factory.return_value.get_loader.return_value = mock_loader

        mock_provider = MagicMock()
        mock_provider.generate.return_value = '[{"question": "Q1"}]'
        mock_provider_factory.return_value.get_provider.return_value = mock_provider

        mock_chunker = MagicMock()
        mock_chunker.chunk.return_value = ["Chunk"]
        mock_chunker_factory.return_value.get_chunker.return_value = mock_chunker

        pipeline = QuestionGenerationPipeline()
        questions = pipeline.run(file_path="test.pdf", num_questions=1)

        assert len(questions) == 1
        mock_loader_factory.return_value.get_loader.assert_called_with("test.pdf")
        mock_loader.load.assert_called_with("test.pdf")

    def test_pipeline_run_file_uses_constructor_path(self, mock_load_config, mock_provider_factory, mock_chunker_factory, mock_loader_factory):
        """Test that constructor file_path is used when not provided in run()."""
        mock_loader = MagicMock()
        mock_loader.load.return_value = "Content"
        mock_loader_factory.return_value.get_loader.return_value = mock_loader

        mock_provider = MagicMock()
        mock_provider.generate.return_value = '[]'
        mock_provider_factory.return_value.get_provider.return_value = mock_provider

        mock_chunker = MagicMock()
        mock_chunker.chunk.return_value = ["Chunk"]
        mock_chunker_factory.return_value.get_chunker.return_value = mock_chunker

        pipeline = QuestionGenerationPipeline(file_path="constructor_file.pdf")
        pipeline.run(num_questions=1)

        mock_loader_factory.return_value.get_loader.assert_called_with("constructor_file.pdf")


class TestPipelineConfiguration:
    """Tests for pipeline configuration handling."""

    def test_pipeline_uses_config_question_type(self, mock_load_config, mock_provider_factory, mock_chunker_factory):
        """Test that config question_type is used."""
        mock_provider = MagicMock()
        mock_provider.generate.return_value = '[]'
        mock_provider_factory.return_value.get_provider.return_value = mock_provider

        mock_chunker = MagicMock()
        mock_chunker.chunk.return_value = ["Chunk"]
        mock_chunker_factory.return_value.get_chunker.return_value = mock_chunker

        mock_prompter = MagicMock()
        mock_prompter.build_prompt.return_value = "Prompt"
        
        pipeline = QuestionGenerationPipeline()
        pipeline.prompter = mock_prompter
        pipeline.run(text="Input", num_questions=1)

        # Verify prompt was built with config question_type
        call_kwargs = mock_prompter.build_prompt.call_args[1]
        assert call_kwargs["question_type"] == "short_answer"  # From mock_config

    def test_pipeline_override_question_type(self, mock_load_config, mock_provider_factory, mock_chunker_factory):
        """Test overriding question_type in run()."""
        mock_provider = MagicMock()
        mock_provider.generate.return_value = '[]'
        mock_provider_factory.return_value.get_provider.return_value = mock_provider

        mock_chunker = MagicMock()
        mock_chunker.chunk.return_value = ["Chunk"]
        mock_chunker_factory.return_value.get_chunker.return_value = mock_chunker

        mock_prompter = MagicMock()
        mock_prompter.build_prompt.return_value = "Prompt"

        pipeline = QuestionGenerationPipeline()
        pipeline.prompter = mock_prompter
        pipeline.run(text="Input", num_questions=1, question_type="multiple_choice")

        call_kwargs = mock_prompter.build_prompt.call_args[1]
        assert call_kwargs["question_type"] == "multiple_choice"

    def test_pipeline_override_difficulty(self, mock_load_config, mock_provider_factory, mock_chunker_factory):
        """Test overriding difficulty in run()."""
        mock_provider = MagicMock()
        mock_provider.generate.return_value = '[]'
        mock_provider_factory.return_value.get_provider.return_value = mock_provider

        mock_chunker = MagicMock()
        mock_chunker.chunk.return_value = ["Chunk"]
        mock_chunker_factory.return_value.get_chunker.return_value = mock_chunker

        mock_prompter = MagicMock()
        mock_prompter.build_prompt.return_value = "Prompt"

        pipeline = QuestionGenerationPipeline()
        pipeline.prompter = mock_prompter
        pipeline.run(text="Input", num_questions=1, difficulty="hard")

        call_kwargs = mock_prompter.build_prompt.call_args[1]
        assert call_kwargs["difficulty"] == "hard"

    def test_pipeline_override_num_questions(self, mock_load_config, mock_provider_factory, mock_chunker_factory):
        """Test overriding num_questions in run()."""
        mock_provider = MagicMock()
        mock_provider.generate.return_value = '[]'
        mock_provider_factory.return_value.get_provider.return_value = mock_provider

        mock_chunker = MagicMock()
        mock_chunker.chunk.return_value = ["Chunk"]
        mock_chunker_factory.return_value.get_chunker.return_value = mock_chunker

        mock_prompter = MagicMock()
        mock_prompter.build_prompt.return_value = "Prompt"

        pipeline = QuestionGenerationPipeline()
        pipeline.prompter = mock_prompter
        pipeline.run(text="Input", num_questions=10)

        call_kwargs = mock_prompter.build_prompt.call_args[1]
        assert call_kwargs["num_questions"] == 10


class TestPipelineEdgeCases:
    """Edge case tests for pipeline."""

    def test_pipeline_empty_parser_result(self, mock_load_config, mock_provider_factory, mock_chunker_factory):
        """Test handling of empty parser result."""
        mock_provider = MagicMock()
        mock_provider.generate.return_value = "Invalid output"
        mock_provider_factory.return_value.get_provider.return_value = mock_provider

        mock_chunker = MagicMock()
        mock_chunker.chunk.return_value = ["Chunk"]
        mock_chunker_factory.return_value.get_chunker.return_value = mock_chunker

        pipeline = QuestionGenerationPipeline()
        questions = pipeline.run(text="Input", num_questions=1)

        # Parser returns [] for invalid output
        assert questions == []

    def test_pipeline_malformed_json_from_llm(self, mock_load_config, mock_provider_factory, mock_chunker_factory):
        """Test handling of malformed JSON from LLM."""
        mock_provider = MagicMock()
        mock_provider.generate.return_value = "This is not JSON at all {{{"
        mock_provider_factory.return_value.get_provider.return_value = mock_provider

        mock_chunker = MagicMock()
        mock_chunker.chunk.return_value = ["Chunk"]
        mock_chunker_factory.return_value.get_chunker.return_value = mock_chunker

        pipeline = QuestionGenerationPipeline()
        questions = pipeline.run(text="Input", num_questions=1)

        assert questions == []

    def test_pipeline_partial_questions_generated(self, mock_load_config, mock_provider_factory, mock_chunker_factory):
        """Test when fewer questions generated than requested."""
        mock_provider = MagicMock()
        mock_provider.generate.return_value = '[{"question": "Q1"}]'  # Only 1 question
        mock_provider_factory.return_value.get_provider.return_value = mock_provider

        mock_chunker = MagicMock()
        mock_chunker.chunk.return_value = ["Chunk"]
        mock_chunker_factory.return_value.get_chunker.return_value = mock_chunker

        pipeline = QuestionGenerationPipeline()
        questions = pipeline.run(text="Input", num_questions=5)

        # Should return what was generated (1 question)
        assert len(questions) == 1

    def test_pipeline_truncates_to_requested_num(self, mock_load_config, mock_provider_factory, mock_chunker_factory):
        """Test that results are truncated to requested number."""
        mock_provider = MagicMock()
        # Returns 10 questions but we only want 3
        mock_provider.generate.return_value = '[{"q": "1"}, {"q": "2"}, {"q": "3"}, {"q": "4"}, {"q": "5"}, {"q": "6"}, {"q": "7"}, {"q": "8"}, {"q": "9"}, {"q": "10"}]'
        mock_provider_factory.return_value.get_provider.return_value = mock_provider

        mock_chunker = MagicMock()
        mock_chunker.chunk.return_value = ["Chunk"]
        mock_chunker_factory.return_value.get_chunker.return_value = mock_chunker

        pipeline = QuestionGenerationPipeline()
        questions = pipeline.run(text="Input", num_questions=3)

        assert len(questions) == 3
