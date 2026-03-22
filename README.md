# Automatic Exam Question Generator

[![CI](https://github.com/AmineAitLaamim/automatic-exam-question-generator/actions/workflows/ci.yml/badge.svg)](https://github.com/AmineAitLaamim/automatic-exam-question-generator/actions/workflows/ci.yml)

An AI-powered application that automatically generates exam questions from course materials using Large Language Models (LLMs).

## Features

- 📄 **Multiple File Formats**: PDF, DOCX, PPTX, TXT, and web URLs
- 🤖 **LLM-Powered**: Uses Ollama with local models (llama3.2, qwen2.5, etc.)
- 📝 **Question Types**: Multiple choice, short answer, true/false, essay
- 🎯 **Difficulty Levels**: Easy, medium, hard
- 🚀 **FastAPI Backend**: RESTful API with automatic documentation
- 🎨 **Streamlit UI**: User-friendly web interface

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- [Ollama](https://ollama.ai/) running locally

### Installation

```bash
# Clone the repository
git clone https://github.com/AmineAitLaamim/automatic-exam-question-generator.git
cd automatic-exam-question-generator

# Install dependencies
make install

# Start Ollama (in a separate terminal)
ollama serve
```

### Usage

```bash
# Start the API server
make api

# Start the Streamlit frontend (in a separate terminal)
make frontend
```

Then open http://localhost:8501 in your browser.

## Development

### Run Tests

```bash
make test
```

### Code Quality

```bash
# Lint code
make lint

# Format code
make format

# Run all checks
make check
```

## Project Structure

```
automatic-exam-question-generator/
├── src/
│   ├── api/           # FastAPI routers and schemas
│   ├── data/          # Data loaders and chunkers
│   ├── generation/    # Question generation pipeline
│   ├── providers/     # LLM provider abstraction
│   └── frontend/      # Streamlit UI
├── tests/             # Pytest test suite
├── configs/           # Configuration files
├── data/              # Data directory
└── Makefile           # Build commands
```

## API Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check
- `POST /api/v1/upload/` - Upload course materials
- `POST /api/v1/generate/` - Generate exam questions

## Configuration

Edit `configs/config.yaml` to customize:

```yaml
model:
  provider: ollama
  name: llama3.2:1b
  base_url: http://localhost:11434

chunker:
  strategy: fixed_size
  chunk_size: 1000
  overlap: 100

generation:
  question_type: short_answer
  difficulty: medium
  num_questions: 5
```

## CI/CD

This project uses GitHub Actions for continuous integration:

- **CI Pipeline**: Runs on every push and PR
  - Linting with ruff
  - Formatting check with black
  - Tests on Ubuntu, Windows, and macOS
  - Python 3.11 and 3.12 support