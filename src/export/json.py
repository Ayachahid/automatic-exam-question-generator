import importlib
from pathlib import Path
from .base import BaseExporter
from src.core.logger import get_logger

_json = importlib.import_module("json")

logger = get_logger("export.json")


class JSONExporter(BaseExporter):
    """
    Exports questions to a formatted JSON file.
    Preserves all fields including optional ones (options, explanation).
    """

    def export(self, questions: list[dict], output_path: str) -> str:
        """
        Write questions to a JSON file with pretty-print formatting.

        Args:
            questions:    List of question dicts.
            output_path:  Destination .json file path.

        Returns:
            Absolute path to the exported file.
        """
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "total": len(questions),
            "questions": questions,
        }

        with open(path, "w", encoding="utf-8") as f:
            _json.dump(payload, f, indent=2, ensure_ascii=False)

        logger.info(f"[JSONExporter] Exported {len(questions)} questions → {path}")
        return str(path.absolute())
