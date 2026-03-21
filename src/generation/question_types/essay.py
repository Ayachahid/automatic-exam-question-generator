from typing import Optional
from pydantic import BaseModel, Field

class EssayQuestion(BaseModel):
    """
    Schema for Essay questions.
    Matches the fields expected by the essay prompt and QuestionResponse schema.
    """
    question: str = Field(..., description="The essay question (clear and open-ended)")
    answer: str = Field(..., description="Key points and ideas the answer should cover")
    explanation: Optional[str] = Field(None, description="Detailed explanation or context for the question")
