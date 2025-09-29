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
	python -m venv venv
	@echo "✅ Virtual environment created in 'venv' directory"

install: venv ## Install dependencies from pyproject.toml
	@echo "📦 Installing dependencies..."
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -e .
	@echo "✅ Dependencies installed"

install-dev: install ## Install in development mode with dev dependencies
	@echo "🔧 Installing development dependencies..."
	./venv/bin/pip install -e ".[dev]"
	@echo "✅ Development dependencies installed"

clean-venv: ## Remove virtual environment
	@echo "🗑️  Removing virtual environment..."
	rm -rf venv
	@echo "✅ Virtual environment removed"

# Development Commands
format: ## Format code with black and isort
	@echo "🎨 Formatting code..."
	./venv/bin/black src/ cmd/ tests/ --line-length 88
	./venv/bin/isort src/ cmd/ tests/ --profile black
	@echo "✅ Code formatted"

lint: ## Lint code with flake8
	@echo "🔍 Linting code..."
	./venv/bin/flake8 src/ cmd/ tests/ --max-line-length 88 --extend-ignore E203,W503
	@echo "✅ Linting complete"

type-check: ## Type check with mypy
	@echo "🔎 Type checking..."
	./venv/bin/mypy src/ cmd/ tests/ --ignore-missing-imports
	@echo "✅ Type checking complete"

test: ## Run tests with pytest
	@echo "🧪 Running tests..."
	./venv/bin/pytest tests/ -v --cov=src --cov-report=html --cov-report=term
	@echo "✅ Tests complete"

clean: ## Clean build artifacts
	@echo "🧹 Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
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
	./venv/bin/vivek --help

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