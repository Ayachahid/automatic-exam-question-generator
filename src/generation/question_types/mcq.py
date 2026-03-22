from typing import List
from .base import BaseQuestion
from pydantic import Field


class MCQQuestion(BaseQuestion):
    """
    Schema for Multiple Choice questions.
    Inherits common fields and adds the options list.
    """

    options: List[str] = Field(..., description="List of 4 options for the question")
