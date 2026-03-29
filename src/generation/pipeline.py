from typing import List, Optional
from src.data.loaders.registry import LoaderFactory
from src.data.chunkers.registry import ChunkerFactory
from src.data.cleaner import TextCleaner
from src.generation.prompter import Prompter
from src.generation.parser import QuestionParser
from src.providers.registry import ProviderFactory
from src.core.config import load_config
from src.core.logger import get_logger

logger = get_logger("generation.pipeline")


class QuestionGenerationPipeline:
    def __init__(
        self, config_path: str = "configs/config.yaml", file_path: Optional[str] = None
    ):
        logger.info("Initializing QuestionGenerationPipeline")

        self.config = load_config(config_path)
        self.loader = LoaderFactory()
        self.cleaner = TextCleaner()
        self.chunker = ChunkerFactory().get_chunker(
            chunker_name=self.config.chunker.strategy,
            chunk_size=self.config.chunker.chunk_size,
            overlap=self.config.chunker.overlap,
            model_name=self.config.chunker.model_name,
            similarity_threshold=self.config.chunker.similarity_threshold,
            max_sentences=self.config.chunker.max_sentences,
            min_sentences=self.config.chunker.min_sentences,
            batch_size=self.config.chunker.batch_size,
        )
        self.prompter = Prompter()
        self.parser = QuestionParser()
        self.provider = ProviderFactory().get_provider(
            provider_name=self.config.model.provider,
            base_url=self.config.model.base_url,
            model=self.config.model.name,
        )
        self.file_path = file_path

    def run(
        self,
        file_path: Optional[str] = None,
        text: Optional[str] = None,
        question_type: Optional[str] = None,
        difficulty: Optional[str] = None,
        num_questions: Optional[int] = None,
    ) -> List[dict]:

        logger.info("Starting question generation pipeline")

        # Determine source content
        if file_path:
            logger.info(f"Loading content from file_path: {file_path}")
            raw_content = self.loader.get_loader(file_path).load(file_path)
        elif text:
            logger.info("Using provided raw text input")
            raw_content = text
        elif self.file_path:
            logger.info(f"Using default file_path: {self.file_path}")
            raw_content = self.loader.get_loader(self.file_path).load(self.file_path)
        else:
            raise ValueError(
                "No input source provided (must be file_path, text, or set in constructor)"
            )

        clean_text = self.cleaner.clean(raw_content)
        chunks = self.chunker.chunk(text=clean_text)
        logger.debug(f"Number of chunks created: {len(chunks)}")
        logger.info(f"Processing {len(chunks)} chunks...")  # Debug print

        all_parsed_questions = []
        num_chunks = len(chunks)
        questions_per_chunk = max(1, num_questions // num_chunks)
        remaining_questions = num_questions

        for i, chunk in enumerate(chunks):
            if remaining_questions <= 0:
                break

            logger.info(f"Processing chunk {i+1}/{num_chunks}")

            # For the last chunk, take all remaining needed questions
            current_num = (
                remaining_questions if i == num_chunks - 1 else questions_per_chunk
            )

            logger.debug(f"Generating {current_num} questions for this chunk")

            prompt = self.prompter.build_prompt(
                chunk,
                question_type=(
                    question_type
                    if question_type is not None
                    else self.config.generation.question_type
                ),
                difficulty=(
                    difficulty
                    if difficulty is not None
                    else self.config.generation.difficulty
                ),
                num_questions=current_num,
            )

            raw_output = self.provider.generate(prompt)
            logger.debug("Parsing generated output")
            parsed_questions = self.parser.parse(raw_output)

            # Only add what we need to reach the limit
            parsed_questions = parsed_questions[:remaining_questions]
            all_parsed_questions.extend(parsed_questions)
            remaining_questions -= len(parsed_questions)
            logger.debug(f"Remaining questions to generate: {remaining_questions}")

        logger.info(
            f"Pipeline finished. Total questions generated: {len(all_parsed_questions)}"
        )

        return all_parsed_questions[:num_questions]
