from typing import Optional, Union
from pydantic import BaseModel, Field

class TrueFalseQuestion(BaseModel):
    """
    Schema for True/False questions.
    Matches the fields expected by the true_false prompt and QuestionResponse schema.
    """
    question: str = Field(..., description="The true/false statement")
    answer: Union[str, bool, int] = Field(..., description="The correct answer (True or False)")
    explanation: Optional[str] = Field(None, description="Explanation for why the answer is True or False")
