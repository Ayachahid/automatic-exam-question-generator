class ExamGeneratorError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class InvalidChunkConfigError(ExamGeneratorError):
    def __init__(self, message: str):
        super().__init__(f"Configuration chunker invalide : {message}")

class UnsupportedFormatError(ExamGeneratorError):
    def __init__(self, extension: str):
        supported = [".txt", ".pdf", ".docx", ".pptx"]
        super().__init__(f"Format non supporté : '{extension}'. Formats acceptés : {supported}")

class EmptyDocumentError(ExamGeneratorError):
    def __init__(self, file_path: str):
        super().__init__(f"Le document '{file_path}' est vide ou illisible.")

class FileReadError(ExamGeneratorError):        
    def __init__(self, file_path: str, reason: str = ""):
        super().__init__(f"Impossible de lire '{file_path}' : {reason}")

class ProviderConnectionError(ExamGeneratorError):
    def __init__(self, provider: str, base_url: str):
        super().__init__(f"Connexion impossible à '{provider}' ({base_url}). Lance : ollama serve")

class ProviderTimeoutError(ExamGeneratorError):
    def __init__(self, provider: str, timeout: int):
        super().__init__(f"'{provider}' n'a pas répondu après {timeout}s.")

class PromptNotFoundError(ExamGeneratorError):
    def __init__(self, question_type: str, path: str):
        super().__init__(f"Template introuvable pour '{question_type}' : '{path}'")

class ParseError(ExamGeneratorError):
    def __init__(self, raw_output: str):
        preview = raw_output[:150] + "..." if len(raw_output) > 150 else raw_output
        super().__init__(f"Impossible de parser la sortie du LLM. Aperçu : {preview}")