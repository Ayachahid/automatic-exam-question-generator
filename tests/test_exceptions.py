from src.core.exceptions import (
    ExamGeneratorError,
    InvalidChunkConfigError,
    UnsupportedFormatError,
    EmptyDocumentError,
    FileReadError,
    ProviderConnectionError,
    ProviderTimeoutError,
    PromptNotFoundError,
    ParseError,
)


class TestExamGeneratorError:
    """Tests for base ExamGeneratorError exception."""

    def test_base_exception_message(self):
        """Test that base exception stores message correctly."""
        error = ExamGeneratorError("Test error message")
        assert str(error) == "Test error message"
        assert error.message == "Test error message"

    def test_base_exception_inheritance(self):
        """Test that ExamGeneratorError inherits from Exception."""
        error = ExamGeneratorError("Test")
        assert isinstance(error, Exception)

    def test_base_exception_can_be_caught_as_exception(self):
        """Test that exception can be caught as generic Exception."""
        try:
            raise ExamGeneratorError("Test")
        except Exception as e:
            assert str(e) == "Test"


class TestInvalidChunkConfigError:
    """Tests for InvalidChunkConfigError."""

    def test_invalid_chunk_config_message(self):
        """Test error message format."""
        error = InvalidChunkConfigError("overlap must be positive")
        assert "Configuration chunker invalide" in str(error)
        assert "overlap must be positive" in str(error)

    def test_invalid_chunk_config_inheritance(self):
        """Test inheritance from ExamGeneratorError."""
        error = InvalidChunkConfigError("test")
        assert isinstance(error, ExamGeneratorError)


class TestUnsupportedFormatError:
    """Tests for UnsupportedFormatError."""

    def test_unsupported_format_message(self):
        """Test error message includes extension and supported formats."""
        error = UnsupportedFormatError(".xyz")
        assert ".xyz" in str(error)
        assert ".txt" in str(error)
        assert ".pdf" in str(error)
        assert ".docx" in str(error)
        assert ".pptx" in str(error)

    def test_unsupported_format_inheritance(self):
        """Test inheritance from ExamGeneratorError."""
        error = UnsupportedFormatError(".test")
        assert isinstance(error, ExamGeneratorError)


class TestEmptyDocumentError:
    """Tests for EmptyDocumentError."""

    def test_empty_document_message(self):
        """Test error message includes file path."""
        error = EmptyDocumentError("document.pdf")
        assert "document.pdf" in str(error)
        assert "vide" in str(error) or "empty" in str(error).lower()

    def test_empty_document_inheritance(self):
        """Test inheritance from ExamGeneratorError."""
        error = EmptyDocumentError("test.docx")
        assert isinstance(error, ExamGeneratorError)


class TestFileReadError:
    """Tests for FileReadError."""

    def test_file_read_error_with_reason(self):
        """Test error message with reason."""
        error = FileReadError("file.pdf", "permission denied")
        assert "file.pdf" in str(error)
        assert "permission denied" in str(error)

    def test_file_read_error_without_reason(self):
        """Test error message without reason."""
        error = FileReadError("file.pdf")
        assert "file.pdf" in str(error)

    def test_file_read_error_inheritance(self):
        """Test inheritance from ExamGeneratorError."""
        error = FileReadError("test.txt", "error")
        assert isinstance(error, ExamGeneratorError)


class TestProviderConnectionError:
    """Tests for ProviderConnectionError."""

    def test_provider_connection_message(self):
        """Test error message includes provider and URL."""
        error = ProviderConnectionError("ollama", "http://localhost:11434")
        assert "ollama" in str(error)
        assert "http://localhost:11434" in str(error)
        assert "Connexion impossible" in str(error) or "Connection" in str(error)

    def test_provider_connection_inheritance(self):
        """Test inheritance from ExamGeneratorError."""
        error = ProviderConnectionError("test-provider", "http://test.com")
        assert isinstance(error, ExamGeneratorError)


class TestProviderTimeoutError:
    """Tests for ProviderTimeoutError."""

    def test_provider_timeout_message(self):
        """Test error message includes provider and timeout."""
        error = ProviderTimeoutError("ollama", 600)
        assert "ollama" in str(error)
        assert "600" in str(error)
        assert "s" in str(error)  # seconds indicator

    def test_provider_timeout_inheritance(self):
        """Test inheritance from ExamGeneratorError."""
        error = ProviderTimeoutError("test", 120)
        assert isinstance(error, ExamGeneratorError)


class TestPromptNotFoundError:
    """Tests for PromptNotFoundError."""

    def test_prompt_not_found_message(self):
        """Test error message includes question type and path."""
        error = PromptNotFoundError("essay", "configs/prompts/essay.txt")
        assert "essay" in str(error)
        assert "configs/prompts/essay.txt" in str(error)

    def test_prompt_not_found_inheritance(self):
        """Test inheritance from ExamGeneratorError."""
        error = PromptNotFoundError("mcq", "path/to/prompt")
        assert isinstance(error, ExamGeneratorError)


class TestParseError:
    """Tests for ParseError."""

    def test_parse_error_short_output(self):
        """Test error message with short raw output."""
        raw = "This is not JSON"
        error = ParseError(raw)
        assert "This is not JSON" in str(error)
        assert "LLM" in str(error)

    def test_parse_error_long_output_truncated(self):
        """Test that long raw output is truncated."""
        raw = "A" * 200
        error = ParseError(raw)
        error_str = str(error)
        # Should be truncated to ~150 chars + "..."
        assert "..." in error_str
        # The preview should contain many As but be less than original + message
        assert len(error_str) < 250

    def test_parse_error_exact_boundary(self):
        """Test truncation at exact boundary."""
        raw = "A" * 150  # Exactly at boundary
        error = ParseError(raw)
        error_str = str(error)
        # Should not be truncated
        assert "A" * 140 in error_str

    def test_parse_error_inheritance(self):
        """Test inheritance from ExamGeneratorError."""
        error = ParseError("invalid output")
        assert isinstance(error, ExamGeneratorError)


class TestExceptionHierarchy:
    """Tests for exception hierarchy."""

    def test_all_exceptions_are_exam_generator_errors(self):
        """Test that all custom exceptions inherit from ExamGeneratorError."""
        exceptions = [
            InvalidChunkConfigError("test"),
            UnsupportedFormatError(".test"),
            EmptyDocumentError("test.txt"),
            FileReadError("test.txt", "error"),
            ProviderConnectionError("ollama", "http://localhost"),
            ProviderTimeoutError("ollama", 60),
            PromptNotFoundError("type", "path"),
            ParseError("output"),
        ]

        for exc in exceptions:
            assert isinstance(exc, ExamGeneratorError)

    def test_all_exceptions_are_exceptions(self):
        """Test that all custom exceptions can be caught as Exception."""
        exceptions = [
            InvalidChunkConfigError("test"),
            UnsupportedFormatError(".test"),
            EmptyDocumentError("test.txt"),
        ]

        for exc in exceptions:
            assert isinstance(exc, Exception)

    def test_catch_all_custom_exceptions(self):
        """Test catching all custom exceptions as ExamGeneratorError."""

        def raise_each():
            raise InvalidChunkConfigError("test")

        def raise_unsupported():
            raise UnsupportedFormatError(".xyz")

        def raise_empty():
            raise EmptyDocumentError("test.pdf")

        for func in [raise_each, raise_unsupported, raise_empty]:
            try:
                func()
            except ExamGeneratorError:
                pass  # Expected
