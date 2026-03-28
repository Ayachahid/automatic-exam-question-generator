from typing import Literal
from .base import BaseExporter
from .json import JSONExporter
from .docx import DOCXExporter
from .pdf import PDFExporter

# Supported export formats
ExportFormat = Literal["json", "docx", "pdf"]

EXPORTER_REGISTRY: dict[str, type[BaseExporter]] = {
    "json": JSONExporter,
    "docx": DOCXExporter,
    "pdf": PDFExporter,
}


class ExporterFactory:
    """
    Factory that returns the correct BaseExporter subclass
    based on the requested format string.
    """

    def get_exporter(self, fmt: str) -> BaseExporter:
        """
        Instantiate and return an exporter for the given format.

        Args:
            fmt: One of "json", "docx", "pdf".

        Returns:
            An instance of the matching BaseExporter subclass.

        Raises:
            ValueError: If the format is not supported.
        """
        fmt = fmt.lower().strip()
        if fmt not in EXPORTER_REGISTRY:
            raise ValueError(
                f"Unsupported export format: '{fmt}'. "
                f"Available: {list(EXPORTER_REGISTRY.keys())}"
            )
        return EXPORTER_REGISTRY[fmt]()

    @staticmethod
    def supported_formats() -> list[str]:
        """Return the list of supported export format keys."""
        return list(EXPORTER_REGISTRY.keys())
