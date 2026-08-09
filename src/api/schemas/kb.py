from typing import List, Optional
from pydantic import BaseModel, Field
from src.api.schemas.request import QuestionType, Difficulty


class IndexRequest(BaseModel):
    file_paths: List[str] = Field(..., description="List of file paths to index")


class IndexResponse(BaseModel):
    message: str
    indexed_files: List[str]
    total_chunks: int


class RAGGenerateRequest(BaseModel):
    query: str = Field(
        ..., description="The subject or topic to generate questions about"
    )
    question_type: QuestionType = Field(default=QuestionType.MULTIPLE_CHOICE)
    difficulty: Difficulty = Field(default=Difficulty.MEDIUM)
    num_questions: int = Field(default=5, ge=1, le=50)
    n_results: int = Field(
        default=3, ge=1, le=10, description="Number of context chunks to retrieve"
    )


class KBResetResponse(BaseModel):
    message: str
