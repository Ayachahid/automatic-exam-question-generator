import yaml
from dataclasses import dataclass


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
    with open(path, "r") as f:
        raw = yaml.safe_load(f)

    return AppConfig(
        model=ModelConfig(**raw["model"]),
        chunker=ChunkerConfig(**raw["chunker"]),
        generation=GenerationConfig(**raw["generation"]),
    )