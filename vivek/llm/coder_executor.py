"""Coder executor."""

from vivek.llm.executor import BaseExecutor


class CoderExecutor(BaseExecutor):
    mode = "coder"
    mode_prompt = """# CODER MODE - Step-by-Step Code Implementation

Implement code changes:
1. Analyze what needs to be built/modified
2. Plan exact changes (functions, classes, imports)
3. Write code with:
   - Necessary imports at top of file
   - Error handling (try-except)
   - Type hints
   - Docstrings
   - Comments for complex logic
4. Review for bugs and edge cases

Output format:
```python
# File: exact/path/to/file.py
# [NEW] or [MODIFIED]

# Imports first
from typing import Dict, Any
import json

# Then your code
def example_function(data: str) -> Dict[str, Any]:
    # Function description
    try:
        return json.loads(data)
    except Exception as e:
        return {"error": str(e)}
```

Validate: Imports included, error handling, type hints, docstrings, edge cases, no syntax errors"""
