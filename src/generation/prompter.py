from pathlib import Path

PROMPTS_DIR = Path(__file__).parent.parent.parent / "configs" / "prompts"


class Prompter:
    def __init__(self):
        self._templates = {}
        # Map question types from code to file names in configs/prompts
        self._type_mapping = {
            "multiple_choice": "mcq",
            "true_false": "true_false",
            "short_answer": "short_answer",
            "essay": "essay",
            "scenario_based": "scenario-based",
        }

    def _load_templates(self, question_type: str) -> str:
        # Standardize and map to file names
        question_type = question_type.replace(" ", "_").lower()
        file_name = self._type_mapping.get(question_type, question_type)

        if file_name in self._templates:
            return self._templates[file_name]

        path = PROMPTS_DIR / f"{file_name}.txt"

        if not path.exists():
            raise FileNotFoundError(
                f"No prompt file found at: {path} for question type: {question_type}"
            )

        template = path.read_text(encoding="utf-8")
        self._templates[file_name] = template
        return template

    def build_prompt(
        self, chunk: str, question_type: str, difficulty: str, num_questions: int
    ) -> str:
        template = self._load_templates(question_type)
        return template.format(
            chunk=chunk, difficulty=difficulty, num_questions=num_questions
        )
