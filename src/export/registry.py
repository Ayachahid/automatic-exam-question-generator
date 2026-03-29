from typing import Literal
from .base import BaseExporter
from .json import JSONExporter
from .docx import DOCXExporter
from .pdf import PDFExporter
from src.core.logger import get_logger

logger = get_logger("src.export.registry")
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
        logger.info(f"Requested exporter format: {fmt}")
        fmt = fmt.lower().strip()
        if fmt not in EXPORTER_REGISTRY:
            logger.error(f"Unsupported export format requested: {fmt}")
            raise ValueError(
                f"Unsupported export format: '{fmt}'. "
                f"Available: {list(EXPORTER_REGISTRY.keys())}"
            )
        exporter_class = EXPORTER_REGISTRY[fmt]
        logger.debug(f"Selected exporter class: {exporter_class.__name__}")

        exporter = exporter_class()

        logger.info(f"Exporter instantiated successfully: {exporter_class.__name__}")
        return exporter

    @staticmethod
    def supported_formats() -> list[str]:
        """Return the list of supported export format keys."""
        logger = get_logger("data.exporter.factory")
        logger.debug("Retrieving supported export formats")
        return list(EXPORTER_REGISTRY.keys())
