# Question Types & Registry

The system supports multiple question formats through a robust inheritance model and a centralized registry.

## 1. Inheritance Model (`base.py`)

All question types inherit from `BaseQuestion` (defined in `src/generation/question_types/base.py`). This base class provides:
- **Common Fields:** `id`, `text`, `type`, `difficulty`, `context`.
- **Validation Logic:** Standard Pydantic validation to ensure every question is well-formed.
- **Serialization:** Methods to convert the question to JSON or other formats.

## 2. Supported Question Types

Each type is implemented in its own file within `src/generation/question_types/`:

- **MCQ (Multiple Choice):** Includes `options` (A, B, C, D) and `correct_answer`.
- **Essay:** Focuses on open-ended prompts and potential `key_points` for grading.
- **Short Answer:** Similar to Essay but with a more concise expected response.
- **True/False:** Normalizes various LLM outputs (Yes/No, 1/0, True/False) into a standard boolean.
- **Scenario-Based:** Provides a complex context or "story" followed by one or more questions.

## 3. The Registry (`registry.py`)

The `QUESTION_REGISTRY` is a mapping that links a type name (e.g., "multiple_choice") to its implementation class.

### Why use a Registry?
- **Dynamic Instantiation:** The API can receive a string `"mcq"` and the system automatically knows to use the `MCQQuestion` model.
- **Extensibility:** To add a new question type (e.g., "Matching"), you simply:
    1. Create `matching.py` inheriting from `BaseQuestion`.
    2. Register it in `registry.py`.
    3. Add a corresponding prompt template in `configs/prompts/`.

## 4. Usage in API

When the `/generate` endpoint is called, the request body includes a `question_type`. The pipeline uses the registry to:
1. Fetch the correct prompt template.
2. Instantiate the correct Pydantic model for parsing the LLM response.
