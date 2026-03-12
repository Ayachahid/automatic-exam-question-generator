from src.data.loaders.registry import LoaderFactory
from src.data.chunkers.registry import ChunkerFactory
from src.generation.prompter import Prompter
from src.providers.ollama import OllamaProvider
from src.core.config import AppConfig, load_config

class QuestionGenerationPipline:
    def __init__(self, config_path: str = "configs/config.yaml", file_path=None):
        self.config     = load_config(config_path)
        self.loader     = LoaderFactory()
        # self.cleaner  = TextCleaner()                     # TODO: add TextCleaner()
        self.chunker    = ChunkerFactory().get_chunker()    # TODO: add config.chunker
        self.prompter   = Prompter()
        self.provider   = OllamaProvider(
            base_url=self.config.model.base_url,
            model=self.config.model.name)
        # self.parser     = QuestionParser()                # TODO: QuestionParser()
        self.file_path = file_path

    def run(self, file_path = None,
            question_type = None,
            difficulty = None,
            num_questions = None):
        file_path = file_path or self.file_path
        if not file_path:
            raise ValueError("No file_path provided")
        
        all_questions = []
        raw_text = self.loader.get_loader(file_path).load(file_path)
        # clean_text = self.cleaner.clean(raw_text) 
        chunks = self.chunker.chunk(text=raw_text)
        print(f"there are {len(chunks)} chunks") # print for DEBUG
        for chunk in chunks:




            prompt = self.prompter.build_prompt(
                chunk,
                question_type   = question_type if question_type is not None else self.config.generation.question_type,
                difficulty      = difficulty    if difficulty    is not None else self.config.generation.difficulty,
                num_questions   = num_questions if num_questions is not None else self.config.generation.num_questions
            )

            provided_result = self.provider.generate(prompt)
            all_questions.append(provided_result)
        # TODO : parser
        

        return all_questions
