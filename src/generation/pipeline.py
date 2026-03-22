from typing import List, Optional
from src.data.loaders.registry import LoaderFactory
from src.data.chunkers.registry import ChunkerFactory
from src.data.cleaner import TextCleaner    
from src.generation.prompter import Prompter
from src.generation.parser import QuestionParser
from src.generation.question_types.registry import QuestionTypeFactory
from src.providers.registry import ProviderFactory
from src.core.config import load_config

class QuestionGenerationPipeline:
    def __init__(self, config_path: str = "configs/config.yaml", file_path: Optional[str] = None):
        self.config     = load_config(config_path)
        self.loader     = LoaderFactory()
        self.cleaner    = TextCleaner()
        self.chunker    = ChunkerFactory().get_chunker()
        self.prompter   = Prompter()
        self.parser     = QuestionParser()
        self.validator = QuestionTypeFactory()
        self.provider  = ProviderFactory().get_provider(
            provider_name = self.config.model.provider,
            base_url      = self.config.model.base_url,
            model         = self.config.model.name
        )
        self.file_path = file_path

    def run(self, 
            file_path: Optional[str] = None,
            text: Optional[str] = None,
            question_type: Optional[str] = None,
            difficulty: Optional[str] = None,
            num_questions: Optional[int] = None) -> List[dict]:
        
        question_type = question_type if question_type is not None else self.config.generation.question_type
        difficulty    = difficulty    if difficulty    is not None else self.config.generation.difficulty
        num_questions = num_questions if num_questions is not None else self.config.generation.num_questions
        
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
        num_chunks = len(chunks)
        questions_per_chunk = max(1, num_questions // num_chunks)
        remaining_questions = num_questions
        
        for i, chunk in enumerate(chunks):
            if remaining_questions <= 0:
                break
                
            # For the last chunk, take all remaining needed questions
            current_num = remaining_questions if i == num_chunks - 1 else questions_per_chunk
            
            prompt = self.prompter.build_prompt(
                chunk,
                question_type = question_type,
                difficulty = difficulty,
                num_questions = current_num
            )

            raw_output = self.provider.generate(prompt)
            parsed_questions = self.parser.parse(raw_output)

            # Only add what we need to reach the limit
            validated = []
            for q in parsed_questions:
                try:
                    validated_q = self.validator.validate(question_type, q)
                    validated.append(validated_q.model_dump())
                except Exception:
                    validated.append(q)

            validated            = validated[:remaining_questions]
            all_parsed_questions.extend(validated)
            remaining_questions -= len(validated)
        
        return all_parsed_questions[:num_questions]
