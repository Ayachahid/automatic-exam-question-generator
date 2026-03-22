import pytest
from unittest.mock import patch, MagicMock
import httpx
from src.providers.ollama import OllamaProvider
from src.providers.registry import ProviderFactory
from src.core.exceptions import ProviderConnectionError, ProviderTimeoutError


class TestOllamaProvider:
    """Tests for OllamaProvider."""

    def setup_method(self):
        """Set up test fixtures."""
        self.base_url = "http://localhost:11434"
        self.model = "test-model"
        self.provider = OllamaProvider(base_url=self.base_url, model=self.model)

    @patch("src.providers.ollama.httpx.post")
    def test_generate_basic(self, mock_post):
        """Test basic generation."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Generated text"}
        mock_post.return_value = mock_response

        result = self.provider.generate("Test prompt")

        assert result == "Generated text"
        mock_post.assert_called_once()

    @patch("src.providers.ollama.httpx.post")
    def test_generate_request_payload(self, mock_post):
        """Test that correct payload is sent."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Generated"}
        mock_post.return_value = mock_response

        self.provider.generate("Test prompt")

        mock_post.assert_called_with(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": "Test prompt",
                "stream": False
            },
            timeout=600
        )

    @patch("src.providers.ollama.httpx.post")
    def test_generate_with_message_content(self, mock_post):
        """Test generation with message.content format."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "message": {"content": "Message content response"}
        }
        mock_post.return_value = mock_response

        result = self.provider.generate("Test prompt")

        assert result == "Message content response"

    @patch("src.providers.ollama.httpx.post")
    def test_generate_with_error_in_response(self, mock_post):
        """Test handling of error in Ollama response."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"error": "Model not found"}
        mock_post.return_value = mock_response

        with pytest.raises(RuntimeError) as exc_info:
            self.provider.generate("Test prompt")

        assert "Ollama API error: Model not found" in str(exc_info.value)

    @patch("src.providers.ollama.httpx.post")
    def test_generate_fallback_to_string(self, mock_post):
        """Test fallback to string conversion for unknown response format."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"unknown_key": "value"}
        mock_post.return_value = mock_response

        result = self.provider.generate("Test prompt")

        assert "unknown_key" in result or "value" in result

    @patch("src.providers.ollama.httpx.post")
    def test_generate_connection_error(self, mock_post):
        """Test ProviderConnectionError on connection failure."""
        mock_post.side_effect = httpx.ConnectError("Connection refused")

        with pytest.raises(ProviderConnectionError) as exc_info:
            self.provider.generate("Test prompt")

        assert "ollama" in str(exc_info.value)
        assert self.base_url in str(exc_info.value)

    @patch("src.providers.ollama.httpx.post")
    def test_generate_timeout_error(self, mock_post):
        """Test ProviderTimeoutError on timeout."""
        mock_post.side_effect = httpx.TimeoutException("Request timed out")

        with pytest.raises(ProviderTimeoutError) as exc_info:
            self.provider.generate("Test prompt")

        assert "ollama" in str(exc_info.value)
        assert "600" in str(exc_info.value)

    @patch("src.providers.ollama.httpx.post")
    def test_generate_custom_timeout(self, mock_post):
        """Test generation with custom timeout."""
        provider = OllamaProvider(
            base_url=self.base_url,
            model=self.model,
            timeout=300
        )

        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Generated"}
        mock_post.return_value = mock_response

        provider.generate("Test prompt")

        call_kwargs = mock_post.call_args[1]
        assert call_kwargs["timeout"] == 300

    @patch("src.providers.ollama.httpx.post")
    def test_generate_empty_response(self, mock_post):
        """Test handling of empty response."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": ""}
        mock_post.return_value = mock_response

        result = self.provider.generate("Test prompt")

        assert result == ""

    @patch("src.providers.ollama.httpx.post")
    def test_generate_long_response(self, mock_post):
        """Test handling of long response."""
        long_text = "This is a very long response. " * 100
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": long_text}
        mock_post.return_value = mock_response

        result = self.provider.generate("Test prompt")

        assert result == long_text
        assert len(result) > 1000


class TestProviderFactory:
    """Tests for ProviderFactory."""

    def test_get_ollama_provider(self):
        """Test getting OllamaProvider from factory."""
        factory = ProviderFactory()
        provider = factory.get_provider(
            provider_name="ollama",
            base_url="http://localhost:11434",
            model="test-model"
        )

        assert isinstance(provider, OllamaProvider)
        assert provider.model == "test-model"
        assert provider.base_url == "http://localhost:11434"

    def test_get_provider_unknown(self):
        """Test ValueError for unknown provider."""
        factory = ProviderFactory()

        with pytest.raises(ValueError) as exc_info:
            factory.get_provider(
                provider_name="unknown",
                base_url="http://localhost:11434",
                model="test-model"
            )

        assert "unknown" in str(exc_info.value)
        assert "ollama" in str(exc_info.value)

    def test_get_provider_custom_url(self):
        """Test getting provider with custom base URL."""
        factory = ProviderFactory()
        provider = factory.get_provider(
            provider_name="ollama",
            base_url="http://remote-server:8080",
            model="llama3"
        )

        assert isinstance(provider, OllamaProvider)
        assert provider.base_url == "http://remote-server:8080"
        assert provider.model == "llama3"

    def test_get_provider_different_models(self):
        """Test getting provider with different model names."""
        factory = ProviderFactory()

        for model_name in ["llama3.2:1b", "qwen2.5:3b", "mistral:7b"]:
            provider = factory.get_provider(
                provider_name="ollama",
                base_url="http://localhost:11434",
                model=model_name
            )
            assert provider.model == model_name
