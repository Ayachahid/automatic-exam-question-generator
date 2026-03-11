from pathlib import Path

PROMPTS_DIR = Path(__file__).parent.parent.parent / "configs" / "prompts"

class Prompter:
    def __init__(self):
        self._templates = {} 

    def _load_templates(self, question_type: str) -> str:
        question_type = question_type.replace(" ", "_")
        
        if question_type in self._templates:
            return self._templates[question_type]

        path = PROMPTS_DIR / f"{question_type}.txt"

        if not path.exists():
            raise FileNotFoundError(
                f"No prompt file for {question_type}"
            )
        
        template = path.read_text(encoding='utf-8')
        self._templates[question_type] = template
        return template

    def build_prompt(self, chunk: str, question_type:str,
                     difficulty: str, num_questions: int) -> str:
        template = self._load_templates(question_type)
        return template.format(
            chunk = chunk,
            difficulty=difficulty,
            num_questions=num_questions
        )