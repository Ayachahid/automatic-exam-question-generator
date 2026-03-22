import httpx
from .base import BaseProvider
from src.core.exceptions import ProviderConnectionError, ProviderTimeoutError


class OllamaProvider(BaseProvider):
    def __init__(self, base_url: str, model: str, timeout: int = 600):
        self.base_url = base_url  # http://localhost:11434
        self.model = model
        self.timeout = timeout

    def generate(self, prompt: str) -> str:
        try:
            response = httpx.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=self.timeout,
            )

        except httpx.ConnectError:
            raise ProviderConnectionError("ollama", self.base_url)

        except httpx.TimeoutException:
            raise ProviderTimeoutError("ollama", self.timeout)

        data = response.json()
        # Handle error responses
        if "error" in data:
            raise RuntimeError(f"Ollama API error: {data['error']}")
        # Handle different response formats
        if "response" in data:
            return data["response"]
        if "message" in data:
            return data["message"]["content"]
        return str(data)
