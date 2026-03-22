from .base import BaseQuestion
from .mcq import MCQQuestion
from .true_false import TrueFalseQuestion
from .short_answer import ShortAnswerQuestion
from .essay import EssayQuestion
from .scenario_based import ScenarioBasedQuestion

QUESTION_REGISTRY = {
    "mcq": MCQQuestion,
    "multiple_choice": MCQQuestion,
    "true_false": TrueFalseQuestion,
    "short_answer": ShortAnswerQuestion,
    "essay": EssayQuestion,
    "scenario_based": ScenarioBasedQuestion,
}


class QuestionTypeFactory:

    def get_model(self, question_type: str):
        if question_type not in QUESTION_REGISTRY:
            raise ValueError(
                f"Type inconnu : '{question_type}'. "
                f"Disponibles : {list(QUESTION_REGISTRY.keys())}"
            )
        return QUESTION_REGISTRY[question_type]

    def validate(self, question_type: str, data: dict) -> BaseQuestion:
        model = self.get_model(question_type)
        return model(**data)
