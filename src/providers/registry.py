from .base   import BaseProvider
from .ollama import OllamaProvider


class ProviderFactory:

    def get_provider(self, provider_name: str, base_url: str, model: str) -> BaseProvider:
        if provider_name == "ollama":
            return OllamaProvider(base_url=base_url, model=model)
        else:
            raise ValueError(
                f"Provider inconnu : '{provider_name}'. "
                "Disponibles : ollama"
            )