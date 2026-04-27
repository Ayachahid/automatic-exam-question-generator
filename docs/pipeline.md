# Generation Pipeline

The generation pipeline is the core workflow that transforms a document into a structured set of exam questions. It follows a rigorous **Load -> Clean -> Chunk -> Prompt -> Generate -> Parse** sequence.

## 1. Sequence of Operations

### Step 1: Loading (`LoaderFactory`)
The system detects the file extension and selects the appropriate loader from `src/data/loaders/`.
- **PDF:** Uses `pdfplumber` or `PyPDF2` to extract text.
- **DOCX:** Uses `python-docx`.
- **PPTX:** Uses `python-pptx`.
- **TXT/Web:** Standard text extraction.

### Step 2: Cleaning (`cleaner.py`)
Raw text often contains noise (extra spaces, headers, footers, page numbers). The cleaner:
- Normalizes whitespace.
- Removes non-printable characters.
- Standardizes encoding.

### Step 3: Chunking (`ChunkerFactory`)
Since LLMs have context window limits, documents are split into "chunks".
- **Fixed Size:** Simple splitting by character/token count.
- **Sentence:** Splitting at sentence boundaries to maintain context.
- **Semantic:** Uses embeddings to group logically related sentences.

### Step 4: Prompting (`Prompter`)
The prompter fetches templates from `configs/prompts/`.
- It maps question types (e.g., `mcq`) to template files (`mcq.txt`).
- It injects the document chunk and any specific instructions into the template.

### Step 5: Generation (`ProviderFactory`)
The request is dispatched to the configured LLM provider (e.g., Ollama).
- The provider handles the communication with the model.
- It returns the raw string response from the LLM.

### Step 6: Parsing (`parser.py`)
Raw LLM output (usually JSON or tagged text) is converted into Pydantic models.
- **Validation:** Ensures the generated question has all required fields (question text, options, correct answer).
- **Correction:** Minor formatting issues are handled here.

## 2. Advanced Pipelines

### RAG Pipeline (`rag_pipeline.py`)
Instead of processing the entire document linearly, the RAG pipeline:
1.  Embeds document chunks into **ChromaDB**.
2.  Searches for the most relevant chunks based on a query or topic.
3.  Generates questions only from the retrieved relevant context.
4.  This is ideal for large knowledge bases where generating from the whole text is impractical.
