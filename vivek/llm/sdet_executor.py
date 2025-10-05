"""SDET executor."""

from vivek.llm.executor import BaseExecutor
from vivek.llm.constants import Mode


class SDETExecutor(BaseExecutor):
    mode = Mode.SDET.value
    mode_prompt = """# SDET MODE - Systematic Testing Approach

Create comprehensive test strategy:
1. Analyze code to understand functionality
2. Identify scenarios: happy path, edge cases, error conditions, boundary values
3. Design tests: input data, expected output, validation criteria
4. Implement tests using:
   - Clear names (test_scenario_description)
   - Arrange-Act-Assert pattern
   - Proper assertions
   - Fixtures/mocks as needed
5. Ensure coverage of all critical paths

Example structure:
```python
import pytest

def test_login_success():
    # Arrange: user = create_user()
    # Act: result = login(user)
    # Assert: assert result.success
```

Validate: All scenarios covered, clear names, proper assertions, edge cases, independent tests"""
