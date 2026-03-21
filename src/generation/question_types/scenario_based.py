from typing import List
from .base import BaseQuestion
from pydantic import Field


class ScenarioBasedQuestion(BaseQuestion):
    """
    Schema for Scenario-Based questions.
    """
    scenario: str       = Field(..., description="The realistic scenario context")
    concepts_tested: List[str] = Field(..., description="Key concepts tested by this question")