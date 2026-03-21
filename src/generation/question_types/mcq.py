from typing import List, Optional
from pydantic import BaseModel, Field

class MCQQuestion(BaseModel):
    """
    Schema for Multiple Choice questions.
    Matches the fields expected by the mcq prompt and QuestionResponse schema.
    """
    question: str = Field(..., description="The multiple choice question")
    options: List[str] = Field(..., description="List of 4 options for the question")
    answer: str = Field(..., description="The correct answer (typically A/B/C/D)")
    explanation: Optional[str] = Field(None, description="Explanation for why the answer is correct")
