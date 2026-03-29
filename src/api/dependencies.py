from functools import lru_cache
from src.generation.pipeline import QuestionGenerationPipeline
from src.core.logger import get_logger

logger = get_logger("api.dependencies")


@lru_cache()
def get_pipeline() -> QuestionGenerationPipeline:
    """
    Returns a singleton instance of the QuestionGenerationPipeline.
    Using lru_cache ensures the pipeline (and its heavy models) is loaded only once.
    """
    logger.info("Initializing QuestionGenerationPipeline (singleton)...")
    pipeline = QuestionGenerationPipeline()
    logger.info("Pipeline initialized successfully")
    return pipeline
