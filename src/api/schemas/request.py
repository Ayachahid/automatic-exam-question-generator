from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, model_validator


class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_ANSWER = "short_answer"
    TRUE_FALSE = "true_false"
    ESSAY = "essay"
    SCENARIO_BASED = "scenario_based"


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class GenerateRequest(BaseModel):
    file_path: Optional[str] = Field(
        None, description="Path to a previously uploaded file."
    )
    text: Optional[str] = Field(
        None, description="Direct text input for question generation."
    )
    question_type: QuestionType = Field(
        default=QuestionType.MULTIPLE_CHOICE,
        description="Type of questions to generate.",
    )
    difficulty: Difficulty = Field(
        default=Difficulty.MEDIUM, description="Difficulty level of the questions."
    )
    num_questions: int = Field(
        default=5, ge=1, le=50, description="Number of questions to generate."
    )

    @model_validator(mode="after")
    def check_input_source(self) -> "GenerateRequest":
        if not self.file_path and not self.text:
            raise ValueError("Either 'file_path' or 'text' must be provided.")

        if self.file_path and self.text:
            raise ValueError(
                "Cannot provide both 'file_path' and 'text'. Please choose one."
            )

        return self
