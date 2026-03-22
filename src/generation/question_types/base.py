from typing import Optional
from pydantic import BaseModel, Field


class BaseQuestion(BaseModel):
    """
    Base schema for all question types.
    Contains common fields shared across different formats.
    """

    question: str = Field(..., description="The exam question text")
    answer: str = Field(..., description="The correct answer or suggested answer")
    explanation: Optional[str] = Field(
        None, description="Detailed explanation or context for the answer"
    )
