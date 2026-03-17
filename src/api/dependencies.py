from functools import lru_cache
from src.generation.pipeline import QuestionGenerationPipline

@lru_cache()
def get_pipeline() -> QuestionGenerationPipline:
    """
    Returns a singleton instance of the QuestionGenerationPipline.
    Using lru_cache ensures the pipeline (and its heavy models) is loaded only once.
    """
    return QuestionGenerationPipline()
