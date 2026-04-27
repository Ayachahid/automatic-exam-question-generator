# Configuration & Prompts

The system is highly configurable, allowing developers to tune the behavior of the LLM, the chunking strategies, and the overall application settings without changing the source code.

## 1. Central Configuration (`configs/config.yaml`)

The main configuration file uses YAML format and is loaded into Pydantic models at runtime (`src/core/config.py`).

### Key Sections:
- **`app`**: General settings like `name`, `version`, and `debug_mode`.
- **`api`**: Network settings (`host`, `port`).
- **`llm`**:
    - `provider`: (e.g., `ollama`, `openai`).
    - `model`: The specific model name (e.g., `llama3`, `mistral`).
    - `temperature`: Controls randomness (0.0 for deterministic, 1.0 for creative).
    - `max_tokens`: Limit on the generated response length.
- **`vector_store`**:
    - `path`: Where ChromaDB stores its data.
    - `embedding_model`: The model used to generate vector representations of text.

## 2. Prompt Management (`configs/prompts/`)

Prompts are stored as individual `.txt` files. This decoupling is critical for "Prompt Engineering."

### Template Variables
Templates use placeholders that the `Prompter` class fills dynamically:
- `{{context}}`: The document text chunk.
- `{{num_questions}}`: How many questions to generate from this chunk.
- `{{difficulty}}`: The requested difficulty level (Easy, Medium, Hard).

### Example Template (`mcq.txt`)
```text
Generate {{num_questions}} Multiple Choice Questions based on the context below.
Context: {{context}}
Difficulty: {{difficulty}}

Format each question as a JSON object with:
- "text": The question
- "options": ["A", "B", "C", "D"]
- "correct_answer": The letter of the correct option
```

## 3. Chunker Configurations (`configs/chunkers/`)

Each chunking strategy has its own configuration file (e.g., `semantic.yaml`), allowing you to fine-tune:
- `chunk_size`: Maximum characters/tokens per chunk.
- `chunk_overlap`: How much text to repeat between chunks to maintain context across boundaries.
- `breakpoint_threshold_type`: (For semantic chunking) How to detect logical breaks in the text.
