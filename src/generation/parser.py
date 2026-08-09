import json
import re
from src.core.logger import get_logger
from src.api.schemas.response import QuestionResponse

logger = get_logger("generation.parser")


class QuestionParser:
    def parse(self, raw_output: str) -> list[dict]:
        logger.debug("Parsing model output into JSON")
        # Strip markdown fences if present
        cleaned = re.sub(r"```json|```", "", raw_output).strip()

        data = None
        try:
            data = json.loads(cleaned)
            logger.debug("Successfully parsed JSON output")
            if not isinstance(data, list):
                data = [data]
        except json.JSONDecodeError:
            logger.warning("Direct JSON parsing failed, trying fallback extraction")
            # Try to extract JSON array from within a longer string
            match = re.search(r"\[.*\]", cleaned, re.DOTALL)
            if match:
                try:
                    extracted = json.loads(match.group())
                    data = extracted if isinstance(extracted, list) else [extracted]
                    logger.debug("Fallback JSON extraction succeeded")
                except json.JSONDecodeError:
                    logger.error("Fallback JSON extraction failed")

        if not data:
            logger.error("Unparseable model output")
            return []

        valid_data = []
        for q in data:
            try:
                # Patch frequent LLM hallucination where essay answers are outputted as a list array
                if "answer" in q and isinstance(q["answer"], list):
                    q["answer"] = ", ".join([str(a) for a in q["answer"]])

                # Validate schema natively to ensure pipeline count matches final API count
                QuestionResponse(**q)
                valid_data.append(q)
            except Exception as e:
                logger.warning(
                    f"Discarding improperly formatted question JSON during parse: {e}"
                )
                continue

        return valid_data
