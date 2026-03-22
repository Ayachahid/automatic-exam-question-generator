from abc import ABC, abstractmethod


class BaseProvider(ABC):

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Envoie un prompt au LLM et retourne la réponse.

        Args:
            prompt: le prompt formaté

        Returns:
            Texte généré par le LLM

        Raises:
            ProviderConnectionError : si le service est inaccessible
            ProviderTimeoutError    : si la génération prend trop de temps
        """
