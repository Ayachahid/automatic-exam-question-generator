# Automatic Exam Question Generator - Makefile

.PHONY: install api frontend clean help

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies using uv"
	@echo "  make api        - Run the FastAPI backend using uv run"
	@echo "  make frontend   - Run the Streamlit frontend using uv run"
	@echo "  make clean      - Remove temporary files and caches"

install:
	uv sync

api:
	uv run python -m uvicorn src.api.main:app --reload --host 127.0.0.1 --port 8000

frontend:
	uv run streamlit run src/frontend/app.py --server.port 8501

clean:
	@powershell -Command "Get-ChildItem -Recurse -Filter '__pycache__' | Remove-Item -Recurse -Force"
	@powershell -Command "if (Test-Path .pytest_cache) { Remove-Item -Recurse -Force .pytest_cache }"
	@powershell -Command "if (Test-Path .ruff_cache) { Remove-Item -Recurse -Force .ruff_cache }"
