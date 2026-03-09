from src.data.loaders.registry import LoaderFactory
from src.data.chunkers.registry import ChunkerFactory
from src.generation.prompter import Prompter
from src.providers.ollama import OllamaProvider

class QuestionGenerationPipline:
    def __init__(self): # add config to the args
        self.loader     = LoaderFactory().get_TXTLoader() # TODO add config.file_path
        # self.cleaner  = TextCleaner() # TODO: add TextCleaner()
        self.chunker    = ChunkerFactory().get_chunker() # TODO: add config.chunker
        self.prompter   = Prompter()
        self.provider   = OllamaProvider(base_url='http://localhost:11434', model='llama3.2:1b') # TODO: add config.base_url config.model
        # self.parser     = QuestionParser() # TODO: QuestionParser()

    def run(self, file_path, question_type, difficulty, num_questions):
        all_questions = []
        raw_text = self.loader.load(self.file_path)
        # clean_text = self.cleaner.clean(raw_text) 
        # chunks     = self.chunker.chunk(clean_text)

        # TODO : working with chunks

        prompt = self.prompter.build_prompt(
            raw_text, # it should be chunks
            question_type,
            difficulty,
            num_questions
        )

        raw_out = self.provider.generate(prompt)
        # TODO : parser
        all_questions.extend(raw_out)

        return all_questions

    def put_file_path(self, path: str):
        self.file_path = path