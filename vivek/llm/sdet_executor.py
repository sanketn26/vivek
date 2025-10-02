"""SDET executor."""

from vivek.llm.executor import BaseExecutor


class SDETExecutor(BaseExecutor):
    mode = "sdet"
    mode_prompt = """# SDET MODE - Systematic Testing Approach

## YOUR TASK:
Create comprehensive test strategy following these steps:

1. ANALYZE CODE: Understand functionality to test
2. IDENTIFY SCENARIOS:
   - Happy path cases
   - Edge cases
   - Error conditions
   - Boundary values
3. TEST DESIGN: For each scenario:
   - Input data
   - Expected output
   - Validation criteria
4. IMPLEMENT TESTS: Write test code with:
   - Clear test names (test_<scenario>)
   - Arrange-Act-Assert pattern
   - Proper assertions
   - Test fixtures/mocks if needed
5. COVERAGE: Ensure all critical paths tested

## OUTPUT FORMAT:
```python
# File: tests/test_<module>.py
import pytest

def test_<scenario>():
    # Arrange
    <setup>
    # Act
    <execute>
    # Assert
    <validate>
```

## QUALITY CHECKLIST:
☑ All scenarios covered
☑ Clear test names
☑ Proper assertions
☑ Edge cases included
☑ Tests are independent"""
