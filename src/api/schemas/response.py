from typing import List, Optional, Union
from pydantic import BaseModel, Field

class QuestionResponse(BaseModel):
    question: str
    options: Optional[List[str]] = Field(None, description="List of options for multiple choice questions.")
    answer: Union[str, int]
    explanation: Optional[str] = Field(None, description="Explanation for the correct answer.")

class GenerationResponse(BaseModel):
    questions: List[QuestionResponse]
    total: int = Field(..., description="Total number of questions generated.")

class UploadResponse(BaseModel):
    filename: str
    file_path: str
    file_id: str
