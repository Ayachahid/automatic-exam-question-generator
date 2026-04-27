# API & Frontend

This document explains how the user interacts with the system and how the frontend communicates with the backend.

## 1. Backend API (FastAPI)

The API is structured into routers located in `src/api/routers/`.

### Key Endpoints

- **`POST /upload/`**: Accepts a document file (PDF, DOCX, etc.) and returns a unique `document_id`.
- **`POST /generate/`**: The main generation endpoint.
    - **Input:** `document_id`, `question_type`, `num_questions`, `difficulty`.
    - **Output:** A list of structured question objects.
- **`POST /knowledge-base/`**: Manages the RAG vector store.
    - **Add Document:** Ingests a file into ChromaDB for future retrieval.
    - **Query:** Searches for relevant snippets based on a natural language query.
- **`GET /export/`**: Converts generated questions into a downloadable file (PDF, DOCX, JSON).

## 2. Frontend (React)

The modern frontend is located in `src/frontend/react-app/`.

### Tech Stack
- **Framework:** React with TypeScript.
- **Styling:** Tailwind CSS for responsive and modern UI.
- **State Management:** React Hooks (useState, useEffect) and a centralized API service (`lib/api.ts`).

### Key Features
- **Dashboard:** Overview of uploaded documents and recent generations.
- **Generator Interface:** Configurable settings (difficulty, type, count) with real-time progress indicators.
- **Exam Mode:** An interactive mode where students can "take" the exam. It provides:
    - Interactive MCQ buttons.
    - Immediate feedback for correct/incorrect answers.
    - Score tracking.
- **Settings Sidebar:** Persistent configuration for LLM models and generation parameters.

## 3. Communication Flow

1.  **User Upload:** React sends a `FormData` request to `/upload/`.
2.  **Processing:** Backend returns a `document_id`.
3.  **Generation:** React sends a JSON body to `/generate/`.
4.  **Feedback:** The frontend renders a loading state (spinner/progress bar) while the LLM processes.
5.  **Rendering:** Once received, the JSON list of questions is mapped to `QuestionCard` components.
6.  **Export:** User clicks "Download PDF", and the frontend triggers a GET request to `/export/`, downloading the blob.
