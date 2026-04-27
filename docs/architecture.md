# Architecture Overview

The **Automatic Exam Question Generator** is designed as a modular, distributed system. It separates concerns between the user interface, the API orchestration layer, and the heavy-lifting generation logic.

## 1. High-Level Components

### Backend (FastAPI)
Located in `src/api/`, the backend serves as the central hub. It handles:
- **RESTful API Endpoints:** For uploading documents, managing the knowledge base, and triggering generation.
- **Request Validation:** Uses Pydantic schemas (`src/api/schemas/`) to ensure data integrity.
- **Service Orchestration:** Connects the API layer to the internal logic pipelines.

### Generation Core
Located in `src/generation/`, this is the "brain" of the application. It contains:
- **Pipelines:** Orchestrators that manage the flow of data.
- **Question Logic:** Definitions and validation for various question formats.
- **Prompter:** Manages the injection of context into LLM templates.

### Data Layer
Located in `src/data/`, this layer handles everything related to raw document processing:
- **Loaders:** Extracting text from PDF, DOCX, TXT, and PPTX.
- **Chunkers:** Splitting text to respect LLM token limits.
- **Vector Store:** Managing document embeddings for RAG (Retrieval-Augmented Generation) using ChromaDB.

### Frontend (React & Streamlit)
- **React App:** A modern, high-performance UI (`src/frontend/react-app/`) providing a rich user experience, including "Exam Mode".
- **Streamlit App:** A legacy/alternative UI (`src/frontend/app.py`) for rapid prototyping and simple interactions.

## 2. Design Patterns

- **Factory/Registry Pattern:** Used for Loaders, Chunkers, Question Types, and LLM Providers. This allows for easy extension without modifying core logic.
- **Pipeline Pattern:** Encapsulates complex workflows (like generation) into a sequence of reproducible steps.
- **Strategy Pattern:** Different chunking and loading strategies can be swapped at runtime via configuration.
