# Vivek AI Assistant - Development Makefile
.PHONY: help venv install install-dev clean clean-venv clean-all format lint type-check test run setup check-ollama install-models

# Default target
help: ## Show this help message
	@echo "🤖 Vivek AI Assistant - Development Commands"
	@echo ""
	@echo "Virtual Environment Management:"
	@echo "  venv        Create virtual environment"
	@echo "  install     Install dependencies from pyproject.toml"
	@echo "  install-dev Install in development mode with dev dependencies"
	@echo "  clean-venv  Remove virtual environment"
	@echo ""
	@echo "Development Commands:"
	@echo "  format      Format code with black and isort"
	@echo "  lint        Lint code with flake8"
	@echo "  type-check  Type check with mypy"
	@echo "  test        Run tests with pytest"
	@echo "  clean       Clean build artifacts"
	@echo "  clean-all   Clean everything (build artifacts + venv)"
	@echo ""
	@echo "Project-Specific Commands:"
	@echo "  setup       Setup development environment"
	@echo "  run         Run the Vivek CLI application"
	@echo "  check-ollama Check if Ollama is running"
	@echo "  install-models Install recommended AI models"
	@echo ""
	@echo "Use 'make <target>' to run commands."

# Virtual Environment Management
venv: ## Create virtual environment
	@echo "🏗️  Creating virtual environment..."
	@# Try to find Python 3.10+ in order of preference
	@if command -v python3.13 >/dev/null 2>&1; then \
		echo "Using python3.13"; \
		python3.13 -m venv venv; \
	elif command -v python3.12 >/dev/null 2>&1; then \
		echo "Using python3.12"; \
		python3.12 -m venv venv; \
	elif command -v python3.11 >/dev/null 2>&1; then \
		echo "Using python3.11"; \
		python3.11 -m venv venv; \
	elif command -v python3.10 >/dev/null 2>&1; then \
		echo "Using python3.10"; \
		python3.10 -m venv venv; \
	elif python3 --version 2>&1 | grep -qE 'Python 3\.(1[0-9]|[2-9][0-9])'; then \
		echo "Using python3 ($(python3 --version))"; \
		python3 -m venv venv; \
	else \
		echo "❌ Python 3.10+ required but not found"; \
		echo "💡 Please install Python 3.10 or higher:"; \
		echo "   - macOS: brew install python@3.10"; \
		echo "   - Ubuntu: sudo apt install python3.10"; \
		echo "   - Or download from https://www.python.org/downloads/"; \
		exit 1; \
	fi
	@echo "✅ Virtual environment created in 'venv' directory"

install: venv ## Install dependencies from pyproject.toml
	@echo "📦 Installing dependencies..."
	@./venv/bin/pip install --upgrade pip || { echo "❌ Failed to upgrade pip"; exit 1; }
	@./venv/bin/pip install -e . || { echo "❌ Failed to install dependencies"; exit 1; }
	@echo "✅ Dependencies installed"

install-dev: install ## Install in development mode with dev dependencies
	@echo "🔧 Installing development dependencies..."
	@./venv/bin/pip install -e ".[dev]" || { echo "❌ Failed to install dev dependencies"; exit 1; }
	@echo "✅ Development dependencies installed"

clean-venv: ## Remove virtual environment
	@echo "🗑️  Removing virtual environment..."
	rm -rf venv
	@echo "✅ Virtual environment removed"

# Development Commands
format: ## Format code with black and isort
	@echo "🎨 Formatting code..."
	@if [ -d "venv" ]; then \
		./venv/bin/black src/ tests/ --line-length 88 2>/dev/null || echo "⚠️  black not installed, run 'make install-dev'"; \
	else \
		echo "❌ Virtual environment not found. Run 'make install-dev' first"; \
		exit 1; \
	fi
	@echo "✅ Code formatted"

lint: ## Lint code with flake8
	@echo "🔍 Linting code..."
	@if [ -d "venv" ]; then \
		./venv/bin/flake8 src/ tests/ --max-line-length 88 --extend-ignore E203,W503 2>/dev/null || echo "⚠️  flake8 not installed, run 'make install-dev'"; \
	else \
		echo "❌ Virtual environment not found. Run 'make install-dev' first"; \
		exit 1; \
	fi
	@echo "✅ Linting complete"

type-check: ## Type check with mypy
	@echo "🔎 Type checking..."
	@if [ -d "venv" ]; then \
		./venv/bin/mypy src/ --ignore-missing-imports 2>/dev/null || echo "⚠️  mypy not installed, run 'make install-dev'"; \
	else \
		echo "❌ Virtual environment not found. Run 'make install-dev' first"; \
		exit 1; \
	fi
	@echo "✅ Type checking complete"

test: ## Run tests with pytest
	@echo "🧪 Running tests..."
	@if [ -d "venv" ]; then \
		if ./venv/bin/pip show pytest-cov >/dev/null 2>&1; then \
			./venv/bin/pytest tests/ -v --cov=src --cov-report=html --cov-report=term; \
		else \
			echo "⚠️  pytest-cov not installed, running tests without coverage..."; \
			./venv/bin/pytest tests/ -v; \
		fi; \
	else \
		echo "❌ Virtual environment not found. Run 'make install-dev' first"; \
		exit 1; \
	fi
	@echo "✅ Tests complete"

clean: ## Clean build artifacts
	@echo "🧹 Cleaning build artifacts..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name ".coverage" -delete 2>/dev/null || true
	@find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@find . -name "*.pyo" -delete 2>/dev/null || true
	@rm -rf .vivek/checkpoints.db* 2>/dev/null || true
	@echo "✅ Build artifacts cleaned"

clean-all: clean clean-venv ## Clean everything (build artifacts + venv)
	@echo "🧹 Cleaning everything..."
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	@echo "✅ Everything cleaned"

# Project-Specific Commands
setup: ## Setup development environment
	@echo "🚀 Setting up development environment..."
	@if [ ! -d "venv" ]; then \
		echo "Creating virtual environment..."; \
		make venv; \
	fi
	@echo "Installing dependencies..."
	@make install-dev
	@echo "Setting up pre-commit hooks..."
	./venv/bin/pip install pre-commit
	./venv/bin/pre-commit install || echo "⚠️  Pre-commit setup failed, but continuing..."
	@echo "✅ Development environment setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Run 'make check-ollama' to verify Ollama is running"
	@echo "  2. Run 'make install-models' to download recommended models"
	@echo "  3. Run 'make run' to start Vivek"

run: ## Run the Vivek CLI application
	@echo "🤖 Starting Vivek AI Assistant..."
	PYTHONPATH=$(shell pwd)/src ./venv/bin/python src/vivek/cli.py --help

check-ollama: ## Check if Ollama is running
	@echo "🔍 Checking Ollama status..."
	@if command -v ollama >/dev/null 2>&1; then \
		if curl -s http://localhost:11434/api/version >/dev/null 2>&1; then \
			echo "✅ Ollama is running on http://localhost:11434"; \
			echo "📋 Available models:"; \
			ollama list || echo "   (Could not list models)"; \
		else \
			echo "❌ Ollama is not running"; \
			echo "💡 To start Ollama:"; \
			echo "   ollama serve"; \
		fi \
	else \
		echo "❌ Ollama is not installed"; \
		echo "💡 To install Ollama:"; \
		echo "   curl -fsSL https://ollama.com/install.sh | sh"; \
	fi

install-models: ## Install recommended AI models
	@echo "🧠 Installing recommended AI models..."
	@if command -v ollama >/dev/null 2>&1; then \
		if curl -s http://localhost:11434/api/version >/dev/null 2>&1; then \
			echo "📥 Downloading qwen2.5-coder:7b (recommended for coding tasks)..."; \
			ollama pull qwen2.5-coder:7b && echo "✅ qwen2.5-coder:7b installed" || echo "❌ Failed to install qwen2.5-coder:7b"; \
			echo "📥 Downloading deepseek-coder:6.7b (excellent for code generation)..."; \
			ollama pull deepseek-coder:6.7b && echo "✅ deepseek-coder:6.7b installed" || echo "❌ Failed to install deepseek-coder:6.7b"; \
		else \
			echo "❌ Ollama is not running. Start it first with: ollama serve"; \
		fi \
	else \
		echo "❌ Ollama is not installed. Install it first:"; \
		echo "   curl -fsSL https://ollama.com/install.sh | sh"; \
	fi

# Quick development workflow
dev: install-dev format lint type-check ## Quick development setup: install, format, lint, and type-check
	@echo "✅ Quick development setup complete!"

# Safety targets
install-safety: ## Install in development mode (alias for install-dev)
	@make install-dev

quick-start: setup ## Quick start for new developers (alias for setup)
	@echo ""
	@echo "🎉 Quick start complete! You can now:"
	@echo "  • Run 'make run' to see available commands"
	@echo "  • Run 'vivek init' to initialize in a project"
	@echo "  • Run 'vivek chat' to start coding assistance"
