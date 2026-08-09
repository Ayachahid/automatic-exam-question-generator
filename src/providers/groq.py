import httpx
from .base import BaseProvider
from src.core.exceptions import ProviderConnectionError, ProviderTimeoutError
from src.core.logger import get_logger

logger = get_logger("providers.groq")


class GroqProvider(BaseProvider):
    def __init__(self, api_key: str, model: str = "llama-3.1-8b-instant", timeout: int = 600):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.base_url = "https://api.groq.com/openai/v1"
        logger.info(f"GroqProvider initialized (model={model})")

    def generate(self, prompt: str) -> str:
        logger.info("Sending request to Groq API")
        try:
            response = httpx.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=self.timeout,
            )
            logger.debug(f"Groq response status: {response.status_code}")
        except httpx.ConnectError:
            logger.error("Failed to connect to Groq")
            raise ProviderConnectionError("groq", self.base_url)
        except httpx.TimeoutException:
            logger.error("Request to Groq timed out")
            raise ProviderTimeoutError("groq", self.timeout)

        data = response.json()

        if "error" in data:
            logger.error(f"Groq API error: {data['error']}")
            raise RuntimeError(f"Groq API error: {data['error']}")

        try:
            content = data["choices"][0]["message"]["content"]
            logger.debug("Groq response received successfully")
            return content
        except (KeyError, IndexError):
            logger.warning("Unexpected Groq response format")
            return str(data)




            