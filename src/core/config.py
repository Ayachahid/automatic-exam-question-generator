import yaml
from dataclasses import dataclass
from typing import Optional
from src.core.logger import get_logger

logger = get_logger("core.config")


@dataclass
class ModelConfig:
    provider: str
    name: str
    base_url: str


@dataclass
class ChunkerConfig:
    strategy: str
    chunk_size: int
    overlap: int
    # Semantic chunker parameters (optional, used when strategy="semantic")
    model_name: Optional[str] = "all-MiniLM-L6-v2"
    similarity_threshold: Optional[float] = 0.75
    max_sentences: Optional[int] = 8
    min_sentences: Optional[int] = 3
    batch_size: Optional[int] = 64


@dataclass
class GenerationConfig:
    question_type: str
    difficulty: str
    num_questions: int


@dataclass
class AppConfig:
    model: ModelConfig
    chunker: ChunkerConfig
    generation: GenerationConfig


def load_config(path: str = "configs/config.yaml") -> AppConfig:
    logger.info(f"Loading config from: {path}")
    with open(path, "r") as f:
        raw = yaml.safe_load(f)

    config = AppConfig(
        model=ModelConfig(**raw["model"]),
        chunker=ChunkerConfig(**raw["chunker"]),
        generation=GenerationConfig(**raw["generation"]),
    )

    logger.info(
        f"Config loaded: provider={config.model.provider} "
        f"model={config.model.name} "
        f"chunker={config.chunker.strategy}"
    )

    return config
