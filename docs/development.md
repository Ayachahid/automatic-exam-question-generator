# Development Guide

This guide provides instructions for setting up the environment, running the application, and contributing to the codebase.

## 1. Environment Setup

The project uses `uv` for ultra-fast dependency management and virtual environment handling.

### Prerequisites:
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) installed
- [Ollama](https://ollama.com/) (if using local LLMs)

### Installation:
```bash
# Sync dependencies and create virtual environment
make install
```

## 2. Running the Application

The project includes a `Makefile` to simplify common tasks.

### Start the Backend:
```bash
make api
# Runs FastAPI at http://127.0.0.1:8000
```

### Start the Frontend:
```bash
make frontend
# Runs Streamlit at http://localhost:8501
```

### Clean Caches:
```bash
make clean
# Removes __pycache__, .pytest_cache, and other temporary files.
```

## 3. Testing Strategy

The project uses `pytest` for all levels of testing.

### Run all tests:
```bash
uv run pytest
```

### Test Categories:
- **Unit Tests (`tests/test_*.py`):** Test individual components like loaders, chunkers, and parsers in isolation.
- **API Tests (`tests/test_api.py`):** Test endpoint responses using FastAPI's `TestClient`.
- **Integration Tests:** Verify the full pipeline flow from document upload to question generation.

## 4. Code Standards

- **Linting & Formatting:** The project uses `ruff`.
- **Typing:** Strict type hints are used across the codebase.
- **Pydantic:** All data models must inherit from `BaseModel` for validation.

## 5. Adding New Features

### Adding a new Document Loader:
1. Create a new file in `src/data/loaders/` (e.g., `markdown.py`).
2. Inherit from `BaseLoader`.
3. Implement the `load()` method.
4. Register the extension in `src/data/loaders/registry.py`.
