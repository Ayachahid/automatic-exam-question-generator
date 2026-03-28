from abc import ABC, abstractmethod


class BaseExporter(ABC):

    @abstractmethod
    def export(self, questions: list[dict], output_path: str) -> str:
        """
        Export a list of questions to a file.

        Args:
            questions:    List of question dicts.
            output_path:  Destination file path with extension.

        Returns:
            Absolute path to the exported file as a string.

        Raises:
            ExportError: If export fails for any reason.
        """
        raise NotImplementedError
