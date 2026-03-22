from functools import lru_cache
from src.generation.pipeline import QuestionGenerationPipeline


@lru_cache()
def get_pipeline() -> QuestionGenerationPipeline:
    """
    Returns a singleton instance of the QuestionGenerationPipeline.
    Using lru_cache ensures the pipeline (and its heavy models) is loaded only once.
    """
    return QuestionGenerationPipeline()
