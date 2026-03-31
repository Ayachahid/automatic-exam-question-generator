from typing import List, Optional, Union
from pydantic import BaseModel, Field


class QuestionResponse(BaseModel):
    question: str
    options: Optional[List[str]] = Field(
        None, description="List of options for multiple choice questions."
    )
    answer: Union[str, int]
    explanation: Optional[str] = Field(
        None, description="Explanation for the correct answer."
    )
    scenario: Optional[str] = Field(
        None, description="Realistic context paragraph (scenario_based only)."
    )
    concepts_tested: Optional[List[str]] = Field(
        None,
        description="Key concepts assessed by this question (scenario_based only).",
    )


class GenerationResponse(BaseModel):
    questions: List[QuestionResponse]
    total: int = Field(..., description="Total number of questions generated.")


class UploadResponse(BaseModel):
    filename: str
    file_path: str
    file_id: str
