# Setup Guide

## Prerequisites

- Python 3.11+
- Poetry (recommended) or pip

## Installation

### 1. Install with Poetry

```bash
# Update lock file
poetry lock

# Install dependencies
poetry install

# Activate environment
poetry shell
```

### 2. Verify Installation

```bash
# Run tests
make test

# Should show: 183+ tests passing
```

## Common Issues

### "Could not parse version constraint"

**Fixed!** The `pyproject.toml` is now properly configured for Poetry.

If you still see this:
```bash
rm poetry.lock
poetry lock
poetry install
```

### Missing Dependencies

```bash
# Install optional dependencies
poetry add sentence-transformers torch

# Or update all
poetry update
```

### Pre-commit Failures

```bash
# Reinstall hooks
poetry run pre-commit install
poetry run pre-commit run --all-files
```

### Old venv Conflicts

```bash
# Clean slate
rm -rf venv/
poetry env remove --all
poetry install
```

## Development Setup

```bash
# 1. Install with dev dependencies
poetry install

# 2. Install pre-commit hooks
poetry run pre-commit install

# 3. Run tests to verify
make test
```

## Poetry Commands

```bash
# Add package
poetry add package-name

# Update packages
poetry update

# Show installed
poetry show

# Run command
poetry run pytest
```

## Next Steps

1. See [README.md](README.md) for usage
2. Check [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for design details
