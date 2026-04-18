# Automatic Exam Question Generator - Makefile

.PHONY: install api frontend stop-frontend restart-frontend test lint format check clean help

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies using uv"
	@echo "  make api        - Run the FastAPI backend using uv run"
	@echo "  make frontend   - Run the React frontend using npm run dev"
	@echo "  make stop-frontend - Stop the React frontend (kills process on port 5173)"
	@echo "  make restart-frontend - Stop and start the React frontend"
	@echo "  make test       - Run pytest tests"
	@echo "  make lint       - Run ruff linter"
	@echo "  make format     - Format code with black"
	@echo "  make check      - Run all checks (lint, format, test)"
	@echo "  make clean      - Remove temporary files and caches"

install:
	uv sync

api:
	uv run python -m uvicorn src.api.main:app --reload --host 127.0.0.1 --port 8000

frontend:
	cd src/frontend/react-app && npm run dev

stop-frontend:
	@powershell -Command "if (Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue) { Stop-Process -Id (Get-NetTCPConnection -LocalPort 5173).OwningProcess -Force; echo 'Frontend stopped.' } else { echo 'Frontend is not running.' }"

restart-frontend: stop-frontend frontend

test:
	uv run python -m pytest tests/ -v

lint:
	uv run ruff check src/ tests/

format:
	uv run python -m black src/ tests/

check: lint format test

clean:
	@powershell -Command "Get-ChildItem -Recurse -Filter '__pycache__' | Remove-Item -Recurse -Force"
	@powershell -Command "if (Test-Path .pytest_cache) { Remove-Item -Recurse -Force .pytest_cache }"
	@powershell -Command "if (Test-Path .ruff_cache) { Remove-Item -Recurse -Force .ruff_cache }"
