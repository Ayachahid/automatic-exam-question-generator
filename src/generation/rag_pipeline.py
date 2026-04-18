from typing import List, Optional
from src.generation.pipeline import QuestionGenerationPipeline
from src.data.vector_store import VectorStore
from src.core.logger import get_logger

logger = get_logger("generation.rag_pipeline")

class RAGQuestionGenerationPipeline(QuestionGenerationPipeline):
    def __init__(
        self, 
        config_path: str = "configs/config.yaml", 
        vector_store_dir: str = "data/processed/chroma_db"
    ):
        super().__init__(config_path=config_path)
        self.vector_store = VectorStore(persist_directory=vector_store_dir)
        logger.info("RAGQuestionGenerationPipeline initialized")

    def run_rag(
        self,
        query: str,
        question_type: Optional[str] = None,
        difficulty: Optional[str] = None,
        num_questions: int = 5,
        n_results: int = 3
    ) -> List[dict]:
        """
        Generate questions using RAG.
        1. Retrieve relevant context from vector store.
        2. Use retrieved context to generate questions.
        """
        logger.info(f"Running RAG pipeline for query: '{query}'")
        
        # 1. Retrieve context
        context_chunks = self.vector_store.query(query_text=query, n_results=n_results)
        if not context_chunks:
            logger.warning("No relevant context found in vector store.")
            return []

        # Combine chunks into a single context string
        context = "\n\n".join(context_chunks)
        logger.debug(f"Retrieved {len(context_chunks)} chunks for context")

        # 2. Generate questions using the base pipeline's logic but with retrieved context
        # We reuse the prompter and provider from the base class
        prompt = self.prompter.build_prompt(
            context,
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
            num_questions=num_questions,
        )

        raw_output = self.provider.generate(prompt)
        parsed_questions = self.parser.parse(raw_output)

        return parsed_questions[:num_questions]

    def index_files(self, file_paths: List[str]):
        """Index multiple files into the vector store."""
        logger.info(f"Indexing {len(file_paths)} files")
        
        for file_path in file_paths:
            try:
                # Load, clean, and chunk
                raw_content = self.loader.get_loader(file_path).load(file_path)
                clean_text = self.cleaner.clean(raw_content)
                chunks = self.chunker.chunk(text=clean_text)
                
                # Prepare for vector store
                metadatas = [{"source": file_path} for _ in chunks]
                ids = [f"{file_path}_{i}" for i in range(len(chunks))]
                
                self.vector_store.add_documents(
                    texts=chunks,
                    metadatas=metadatas,
                    ids=ids
                )
                logger.info(f"Successfully indexed: {file_path}")
            except Exception as e:
                logger.error(f"Failed to index {file_path}: {e}")
                raise e
