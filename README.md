# Vivek - AI Coding Assistant

Clean architecture AI coding assistant following SOLID principles.

## Quick Start

```bash
# Install dependencies
poetry lock && poetry install

# Run tests
make test

# Use Vivek
vivek init
vivek chat
```

## Project Status

- **Version**: 3.0.0
- **Tests**: 183/194 passing (94%)
- **Architecture**: Clean Architecture with SOLID principles
- **Python**: 3.11+

## Installation

### Using Poetry (Recommended)

```bash
poetry install
poetry shell
```

### Using pip

```bash
pip install -e .
```

## Usage

```bash
# Initialize project
vivek init --model qwen2.5-coder:7b

# Start chat session
vivek chat

# Check status
vivek status
```

## Testing

```bash
# Run all tests
make test

# Run specific tests
pytest tests/test_new_architecture.py -v

# With coverage
pytest tests/ --cov=src/vivek
```

## Architecture

```
src/vivek/
├── domain/          # Business logic (Task, Workflow, Planning)
├── application/     # Use cases (Services, Orchestrators)
├── infrastructure/  # External dependencies (LLM, Persistence, DI)
└── cli.py          # Command-line interface
```

## Documentation

- **[SETUP.md](SETUP.md)** - Setup and installation guide
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Architecture overview
- **[docs/CHANGELOG.md](docs/CHANGELOG.md)** - Version history

## Development

```bash
# Format code
black src/ tests/

# Lint
flake8 src/

# Pre-commit hooks
pre-commit install
pre-commit run --all-files
```

## Contributing

1. Follow SOLID principles
2. Write tests for new features
3. Use Poetry for dependency management
4. Run pre-commit hooks before committing

## License

MIT License - See LICENSE file for details
