# Documentation Index

Welcome to the **Automatic Exam Question Generator** technical documentation. This folder contains detailed explanations of the system's architecture, data processing logic, and user interfaces.

## 📚 Contents

1.  **[Architecture Overview](architecture.md)**
    - High-level structural map of Backend, Frontend, and Core logic.
    - Design patterns (Factory, Pipeline, Registry).

2.  **[Generation Pipeline](pipeline.md)**
    - Step-by-step breakdown: Load -> Clean -> Chunk -> Prompt -> Generate -> Parse.
    - Explanation of RAG (Retrieval-Augmented Generation).

3.  **[Question Types & Registry](question_types.md)**
    - Inheritance model for MCQs, Essays, and True/False.
    - How to extend the system with new question formats.

4.  **[API & Frontend](api_and_frontend.md)**
    - FastAPI endpoint definitions.
    - React frontend structure and "Exam Mode".

## 🛠️ Quick Start for Developers

- **Adding a Loader:** See `src/data/loaders/`.
- **Modifying Prompts:** Check `configs/prompts/`.
- **Adding a Question Type:** Refer to `src/generation/question_types/`.
- **Testing:** Run `pytest` to verify changes against the existing suite.
