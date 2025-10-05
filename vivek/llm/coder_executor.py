"""Coder executor."""

from vivek.llm.executor import BaseExecutor
from vivek.llm.constants import (
    Mode,
    TokenLimits,
    CompressionStrategy,
    OutputFormatMarkers,
    PromptSections,
)


class CoderExecutor(BaseExecutor):
    mode = Mode.CODER.value
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
4. Review for bugs and edge cases"""

    def get_mode_specific_instructions(self) -> str:
        """Get coder-specific instructions for implementation."""
        return """Focus on code quality and best practices:
- Use proper Python conventions (PEP 8)
- Include comprehensive error handling
- Add type hints for all function parameters and return values
- Write clear docstrings explaining functionality
- Add comments for complex business logic
- Consider edge cases and error conditions
- Ensure code is testable and maintainable"""

    def get_mode_specific_process_steps(self) -> str:
        """Get coder-specific process steps."""
        return """1. Execute work items in dependency order (check dependencies array - items with [] go first)
2. For each work item, break into 3-5 sub-tasks (design, implement, test, review)
3. Plan the code structure and interfaces before writing
4. Implement with proper error handling and validation
5. Review for code quality, performance, and edge cases
6. Verify completion: ensure code runs without syntax/runtime errors"""

    def get_mode_specific_output_format(self) -> str:
        """Get coder-specific output format requirements."""
        return f"""{OutputFormatMarkers.OUTPUT_FORMAT} (for each work item):
```
{OutputFormatMarkers.WORK_ITEM_HEADER}

**Implementation Requirements:**
- Use proper Python syntax and conventions
- Include all necessary imports at the top
- Add comprehensive error handling
- Include type hints and docstrings
- Add comments for complex logic

**Code Structure:**
```python
# File: [file_path]
# [NEW] or [MODIFIED]

# Imports (if any)
from typing import Dict, Any
import json

# Your implementation here
def example_function(data: str) -> Dict[str, Any]:
    \"\"\"Function description with details.\"\"\"
    try:
        # Implementation logic
        return json.loads(data)
    except Exception as e:
        # Proper error handling
        return {{"error": str(e)}}
```

**Status Validation:**
- Code syntax is valid
- Error handling is comprehensive
- Type hints are included
- Docstrings explain functionality
- Edge cases are considered
```"""

    def get_context_compression_strategy(self) -> str:
        """Coder mode benefits from recent context to understand current codebase."""
        return CompressionStrategy.RECENT

    def get_max_context_tokens(self) -> int:
        """Coder mode needs more context for code analysis and implementation."""
        return TokenLimits.MAX_CONTEXT_TOKENS + 500  # Extra tokens for code context