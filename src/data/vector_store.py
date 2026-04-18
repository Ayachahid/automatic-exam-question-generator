import chromadb
from chromadb.config import Settings
from typing import List, Optional
from src.core.logger import get_logger
from pathlib import Path

logger = get_logger("data.vector_store")

class VectorStore:
    def __init__(self, persist_directory: str = "data/processed/chroma_db"):
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initializing ChromaDB at {self.persist_directory}")
        self.client = chromadb.PersistentClient(path=str(self.persist_directory))
        self.collection = self.client.get_or_create_collection(name="exam_questions")

    def add_documents(self, texts: List[str], metadatas: List[dict], ids: List[str]):
        """Add documents to the vector store."""
        logger.info(f"Adding {len(texts)} documents to vector store")
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )

    def query(self, query_text: str, n_results: int = 5) -> List[str]:
        """Query the vector store for similar documents."""
        logger.info(f"Querying vector store for: '{query_text}'")
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        # Results is a dictionary with 'documents', 'metadatas', etc.
        # documents is a list of lists of strings
        if results['documents']:
            return results['documents'][0]
        return []

    def reset(self):
        """Reset the collection."""
        logger.warning("Resetting the knowledge base")
        self.client.delete_collection(name="exam_questions")
        self.collection = self.client.get_or_create_collection(name="exam_questions")

    def list_indexed_files(self) -> List[str]:
        """List unique source files currently in the vector store."""
        results = self.collection.get(include=['metadatas'])
        if not results or not results['metadatas']:
            return []
        
        sources = set()
        for meta in results['metadatas']:
            if meta and 'source' in meta:
                # Remove the UUID prefix (e.g., 'uuid_filename.pdf' -> 'filename.pdf')
                filename = Path(meta['source']).name
                if "_" in filename:
                    # The upload router saves files as f"{file_id}_{safe_filename}"
                    # We split only on the first underscore to get the original name
                    parts = filename.split("_", 1)
                    if len(parts) > 1:
                        filename = parts[1]
                sources.add(filename)
        return sorted(list(sources))
