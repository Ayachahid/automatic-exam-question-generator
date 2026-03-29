from .base import BaseProvider
from .ollama import OllamaProvider
from src.core.logger import get_logger

logger = get_logger("providers.factory")


class ProviderFactory:

    def get_provider(
        self, provider_name: str, base_url: str, model: str
    ) -> BaseProvider:

        logger.info(f"Selecting provider: {provider_name}")

        if provider_name == "ollama":
            logger.debug(f"Creating OllamaProvider (model={model})")
            return OllamaProvider(base_url=base_url, model=model)
        else:
            logger.error(f"Unknown provider requested: {provider_name}")
            raise ValueError(
                f"Provider inconnu : '{provider_name}'. " "Disponibles : ollama"
            )
