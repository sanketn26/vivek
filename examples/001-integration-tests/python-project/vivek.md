# Vivek Configuration

## Project Settings
- **Languages**: python
- **Frameworks**: FastAPI, Next.js, React
- **Test Frameworks**: pytest, jest
- **Package Managers**: pip, npm

## LLM Configuration
- **Mode**: hybrid
- **Planner Model**: qwen2.5-coder:7b
- **Executor Model**: qwen2.5-coder-7b-instruct-mlx
- **Fallback Enabled**: True
- **Auto Switch**: True

## Preferences
- **Default Mode**: peer
- **Search Enabled**: True
- **Auto Index**: True
- **Privacy Mode**: False

## Ignored Paths
- node_modules/
- .git/
- __pycache__/
- .env
- *.pyc
- dist/
- build/

## Custom Instructions
- Focus on clean, maintainable code with good test coverage.
- Prefer explicit imports and clear variable names.
- Always include error handling for external API calls.
