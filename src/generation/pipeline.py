from typing import List, Optional
from src.data.loaders.registry import LoaderFactory
from src.data.chunkers.registry import ChunkerFactory
from src.data.cleaner import TextCleaner    
from src.generation.prompter import Prompter
from src.generation.parser import QuestionParser
from src.providers.ollama import OllamaProvider
from src.core.config import AppConfig, load_config

class QuestionGenerationPipeline:
    def __init__(self, config_path: str = "configs/config.yaml", file_path: Optional[str] = None):
        self.config     = load_config(config_path)
        self.loader     = LoaderFactory()
        self.cleaner    = TextCleaner()
        self.chunker    = ChunkerFactory().get_chunker()
        self.prompter   = Prompter()
        self.parser     = QuestionParser()
        self.provider   = OllamaProvider(
            base_url=self.config.model.base_url,
            model=self.config.model.name
        )
        self.file_path = file_path

    def run(self, 
            file_path: Optional[str] = None,
            text: Optional[str] = None,
            question_type: Optional[str] = None,
            difficulty: Optional[str] = None,
            num_questions: Optional[int] = None) -> List[dict]:
        
        # Determine source content
        if file_path:
            raw_content = self.loader.get_loader(file_path).load(file_path)
        elif text:
            raw_content = text
        elif self.file_path:
            raw_content = self.loader.get_loader(self.file_path).load(self.file_path)
        else:
            raise ValueError("No input source provided (must be file_path, text, or set in constructor)")
        
        clean_text = self.cleaner.clean(raw_content)
        chunks = self.chunker.chunk(text=clean_text)
        print(f"Processing {len(chunks)} chunks...") # Debug print

        all_parsed_questions = []
        for chunk in chunks:
            prompt = self.prompter.build_prompt(
                chunk,
                question_type   = question_type if question_type is not None else self.config.generation.question_type,
                difficulty      = difficulty    if difficulty    is not None else self.config.generation.difficulty,
                num_questions   = num_questions if num_questions is not None else self.config.generation.num_questions
            )

            raw_output = self.provider.generate(prompt)
            parsed_questions = self.parser.parse(raw_output)
            all_parsed_questions.extend(parsed_questions)
        
        return all_parsed_questions
