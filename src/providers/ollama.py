import httpx
from .base import BaseProvider
from src.core.exceptions import ProviderConnectionError, ProviderTimeoutError
from src.core.logger import get_logger

logger = get_logger("providers.ollama")


class OllamaProvider(BaseProvider):
    def __init__(self, base_url: str, model: str, timeout: int = 600):
        self.base_url = base_url  # http://localhost:11434
        self.model = model
        self.timeout = timeout

        logger.info(f"OllamaProvider initialized (model={model}, base_url={base_url})")

    def generate(self, prompt: str) -> str:
        logger.info("Sending request to Ollama API")
        try:
            response = httpx.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=self.timeout,
            )

            logger.debug(f"Ollama response status: {response.status_code}")

        except httpx.ConnectError:
            logger.error("Failed to connect to Ollama")
            raise ProviderConnectionError("ollama", self.base_url)

        except httpx.TimeoutException:
            logger.error("Request to Ollama timed out")
            raise ProviderTimeoutError("ollama", self.timeout)

        data = response.json()
        # Handle error responses
        if "error" in data:
            logger.error(f"Ollama API error: {data['error']}")
            raise RuntimeError(f"Ollama API error: {data['error']}")
        # Handle different response formats
        if "response" in data:
            logger.debug("Ollama response received successfully")
            return data["response"]
        if "message" in data:
            logger.debug("Ollama message format received")
            return data["message"]["content"]

        logger.warning("Unexpected Ollama response format")
        return str(data)
