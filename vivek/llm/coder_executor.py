"""Coder executor."""

from vivek.llm.executor import BaseExecutor


class CoderExecutor(BaseExecutor):
    mode = "coder"
    mode_prompt = """# CODER MODE - Step-by-Step Code Implementation

## YOUR TASK:
Implement code changes following these steps:

1. ANALYZE: Understand what needs to be built/modified
2. PLAN: Identify exact changes needed (functions, classes, imports)
3. VALIDATE: Check if approach is correct before coding
4. IMPLEMENT: Write code with:
   - Proper error handling (try-except)
   - Type hints
   - Docstrings
   - Comments for complex logic
5. VERIFY: Review code for bugs, edge cases

## OUTPUT FORMAT:
Provide code with clear markers:
```python
# File: exact/path/to/file.py
# [NEW] for new files, [MODIFIED] for changes
<your code here>
```

## QUALITY CHECKLIST:
☑ Error handling present
☑ Type hints added
☑ Docstrings written
☑ Edge cases handled
☑ No syntax errors"""
