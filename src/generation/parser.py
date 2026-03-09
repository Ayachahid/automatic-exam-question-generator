import json, re
from pydantic import BaseModel

class QuestionParser:
    def parse(self, raw_output: str) -> list[dict]:
        # Strip markdown fences if present
        cleaned = re.sub(r"```json|```", "", raw_output).strip()
        
        try:
            data = json.loads(cleaned)
            return data if isinstance(data, list) else [data]
        except json.JSONDecodeError:
            # Try to extract JSON array from within a longer string
            match = re.search(r'\[.*\]', cleaned, re.DOTALL)
            if match:
                return json.loads(match.group())
            return []  # fallback: return empty if unparseable
        

class MCQQuestion(BaseModel):
    question: str
    options: list[str]
    answer: str
    explanation: str