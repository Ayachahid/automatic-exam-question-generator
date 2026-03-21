from typing import Optional
from pydantic import BaseModel, Field

class ShortAnswerQuestion(BaseModel):
    """
    Schema for Short Answer questions.
    Matches the fields expected by the short_answer prompt and QuestionResponse schema.
    """
    question: str = Field(..., description="The short answer question")
    answer: str = Field(..., description="The correct answer (typically 1-3 sentences)")
    explanation: Optional[str] = Field(None, description="Detailed explanation or context for the answer")
