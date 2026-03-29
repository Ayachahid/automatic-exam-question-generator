import json
import re
from src.core.logger import get_logger

logger = get_logger("generation.parser")


class QuestionParser:
    def parse(self, raw_output: str) -> list[dict]:
        logger.debug("Parsing model output into JSON")
        # Strip markdown fences if present
        cleaned = re.sub(r"```json|```", "", raw_output).strip()

        try:
            data = json.loads(cleaned)
            logger.debug("Successfully parsed JSON output")
            return data if isinstance(data, list) else [data]
        except json.JSONDecodeError:
            logger.warning("Direct JSON parsing failed, trying fallback extraction")
            # Try to extract JSON array from within a longer string
            match = re.search(r"\[.*\]", cleaned, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group())
                    logger.debug("Fallback JSON extraction succeeded")
                    return data
                except json.JSONDecodeError:
                    logger.error("Fallback JSON extraction failed")

            logger.error("Unparseable model output")
            return []  # fallback: return empty if unparseable
