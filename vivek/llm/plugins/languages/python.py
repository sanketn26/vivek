"""Python Language Plugin implementation."""

from typing import Dict, Any, Optional, Type
from dataclasses import dataclass, field

from vivek.llm.plugins.base.language_plugin import LanguagePlugin, LanguageConventions
from vivek.llm.models import LLMProvider
from vivek.llm.constants import Mode


@dataclass
class PythonConventions(LanguageConventions):
    """Python-specific conventions and best practices."""

    def __post_init__(self):
        if not self.language:
            self.language = "python"
        if not self.extensions:
            self.extensions = [".py", ".pyi"]

        # Naming conventions
        if not self.naming_conventions:
            self.naming_conventions = {
                "snake_case": "functions, variables, modules",
                "PascalCase": "classes, exceptions",
                "SCREAMING_SNAKE_CASE": "constants",
                "private": "prefixed with single underscore"
            }

        # Import and dependency management
        if not self.import_style:
            self.import_style = "Separate imports into three groups: standard library, third-party, local modules"
        if not self.dependency_management:
            self.dependency_management = "Use requirements.txt, setup.py, or pyproject.toml with virtual environments"

        # Code style and formatting
        if not self.code_style:
            self.code_style = "Follow PEP 8 style guidelines with 4-space indentation"
        if not self.formatting_rules:
            self.formatting_rules = {
                "line_length": "88 characters (Black default)",
                "indentation": "4 spaces (no tabs)",
                "quotes": "double quotes preferred",
                "trailing_comma": "single trailing comma in multi-line structures"
            }

        # Error handling
        if not self.error_handling:
            self.error_handling = "Use specific exception types with try-except-else-finally blocks"
        if not self.exception_types:
            self.exception_types = [
                "ValueError", "TypeError", "RuntimeError", "IOError",
                "ImportError", "AttributeError", "KeyError", "IndexError"
            ]

        # Documentation
        if not self.documentation_style:
            self.documentation_style = "Google/NumPy style docstrings with Args/Returns/Raises sections"
        if not self.comment_conventions:
            self.comment_conventions = {
                "module": "Triple-quoted strings at top of file",
                "function": "Docstrings with descriptive purpose",
                "inline": "# comments for complex logic",
                "TODO": "# TODO: comments for future improvements"
            }

        # Type system
        if not self.type_system:
            self.type_system = "Dynamic typing with optional static type hints"
        if not self.type_annotations:
            self.type_annotations = "Use typing module for type hints, Optional for nullable values"

        # Testing
        if not self.testing_frameworks:
            self.testing_frameworks = ["unittest", "pytest", "doctest"]
        if not self.testing_patterns:
            self.testing_patterns = {
                "naming": "test_*.py files, test_* functions",
                "assertions": "Use assert statements with descriptive messages",
                "fixtures": "Use pytest fixtures for test setup",
                "coverage": "Aim for >80% test coverage"
            }

        # Project structure
        if not self.project_structure:
            self.project_structure = {
                "src": "Main source code directory",
                "tests": "Test files and fixtures",
                "docs": "Documentation files",
                "requirements.txt": "Python dependencies",
                "setup.py": "Package configuration",
                "README.md": "Project documentation"
            }
        if not self.entry_points:
            self.entry_points = ["main.py", "__main__.py", "cli.py"]

        # Idioms and best practices
        if not self.idioms:
            self.idioms = [
                "Use list/dict comprehensions for readable transformations",
                "Prefer pathlib over os.path for file operations",
                "Use context managers (with statements) for resource management",
                "Follow the single responsibility principle",
                "Use dataclasses for simple data containers"
            ]
        if not self.best_practices:
            self.best_practices = [
                "Write comprehensive docstrings for all public functions",
                "Use virtual environments for dependency isolation",
                "Handle exceptions at the appropriate level",
                "Use type hints for better IDE support and documentation",
                "Follow PEP 8 naming and formatting conventions",
                "Write tests for all non-trivial functionality",
                "Use logging instead of print statements",
                "Prefer composition over inheritance"
            ]


class PythonLanguagePlugin(LanguagePlugin):
    """Python language plugin with comprehensive Python-specific behavior."""

    def __init__(self):
        super().__init__("python")

    @property
    def supported_languages(self) -> list[str]:
        """List of language identifiers this plugin supports."""
        return ["python", "py"]

    @property
    def supported_modes(self) -> list[str]:
        """List of execution modes this plugin supports."""
        return [Mode.CODER.value, Mode.ARCHITECT.value, Mode.PEER.value, Mode.SDET.value]

    @property
    def name(self) -> str:
        """Human-readable name for this plugin."""
        return "Python Language Assistant"

    @property
    def version(self) -> str:
        """Plugin version string."""
        return "1.0.0"

    def get_conventions(self) -> PythonConventions:
        """Get Python-specific conventions for this plugin."""
        if not self._conventions:
            self._conventions = PythonConventions(language=self.language)
        return self._conventions

    def create_executor(self, provider: LLMProvider, mode: str, **kwargs) -> Any:
        """Create a Python and mode-specific executor instance."""
        from vivek.llm.coder_executor import CoderExecutor
        from vivek.llm.architect_executor import ArchitectExecutor
        from vivek.llm.peer_executor import PeerExecutor
        from vivek.llm.sdet_executor import SDETExecutor

        mode_lower = mode.lower()

        class PythonLanguageExecutor:
            """Python-aware executor wrapper with language-specific prompts."""

            def __init__(self, base_executor, language_plugin):
                self.base_executor = base_executor
                self.language_plugin = language_plugin
                self.language = "python"
                self.mode = mode_lower

                # Set language-specific prompt
                if hasattr(base_executor, 'mode_prompt'):
                    base_executor.mode_prompt = f"Python {mode_lower.title()} Mode: {self._get_mode_specific_prompt(mode_lower)}"

            def _get_mode_specific_prompt(self, mode: str) -> str:
                """Get Python-specific prompt for the mode."""
                mode_instructions = self.language_plugin.get_language_specific_instructions(mode)
                return f"Follow Python best practices. {mode_instructions}"

            def __getattr__(self, name):
                """Delegate all other attributes to the base executor."""
                return getattr(self.base_executor, name)

        if mode_lower == Mode.CODER.value:
            base_executor = CoderExecutor(provider)
            return PythonLanguageExecutor(base_executor, self)
        elif mode_lower == Mode.ARCHITECT.value:
            base_executor = ArchitectExecutor(provider)
            return PythonLanguageExecutor(base_executor, self)
        elif mode_lower == Mode.PEER.value:
            base_executor = PeerExecutor(provider)
            return PythonLanguageExecutor(base_executor, self)
        elif mode_lower == Mode.SDET.value:
            base_executor = SDETExecutor(provider)
            return PythonLanguageExecutor(base_executor, self)
        else:
            raise ValueError(f"Unsupported mode for Python plugin: {mode}")

    def get_language_specific_instructions(self, mode: str) -> str:
        """Get Python-specific instructions for the given mode."""
        base_instructions = f"""**Python Language Requirements for {mode.title()} Mode:**

Follow Python conventions:
- Use PEP 8 style guidelines with 4-space indentation
- Include type hints for all function parameters and return values
- Write comprehensive docstrings using Google/NumPy style
- Use pathlib for file operations instead of os.path
- Handle exceptions with specific exception types

"""

        mode_lower = mode.lower()

        if mode_lower == Mode.CODER.value:
            return base_instructions + """
**Coding Requirements:**
- Use explicit imports at the top of files (no wildcard imports)
- Implement proper error handling with try-except blocks
- Use list/dict comprehensions where appropriate
- Follow the single responsibility principle
- Write unit tests for all functions"""
        elif mode_lower == Mode.ARCHITECT.value:
            return base_instructions + """
**Architecture Requirements:**
- Design for scalability using proper abstractions
- Consider async/await patterns for I/O operations
- Plan for testability with dependency injection
- Document API interfaces and data contracts
- Consider deployment and packaging strategies"""
        elif mode_lower == Mode.PEER.value:
            return base_instructions + """
**Code Review Requirements:**
- Check for adherence to PEP 8 and type hints
- Verify proper error handling and edge cases
- Ensure comprehensive docstring coverage
- Review for security vulnerabilities (input validation, etc.)
- Check for appropriate testing coverage"""
        elif mode_lower == Mode.SDET.value:
            return base_instructions + """
**Testing Requirements:**
- Write comprehensive unit tests using pytest
- Include integration and end-to-end tests
- Test edge cases and error conditions
- Use fixtures for test data and setup
- Aim for >80% test coverage"""
        else:
            return base_instructions

    def get_code_example(self, mode: str, context: Optional[str] = None) -> str:
        """Get a Python-specific code example for the given mode."""
        mode_lower = mode.lower()

        if mode_lower == Mode.CODER.value:
            return self._get_python_coder_example()
        elif mode_lower == Mode.ARCHITECT.value:
            return self._get_python_architect_example()
        elif mode_lower == Mode.PEER.value:
            return self._get_python_peer_example()
        elif mode_lower == Mode.SDET.value:
            return self._get_python_sdet_example()
        else:
            return self._get_python_coder_example()

    def _get_python_coder_example(self) -> str:
        """Get Python coder example."""
        return """# File: data_processor.py
# [NEW] or [MODIFIED]

from typing import Dict, List, Optional, Any
from pathlib import Path
import json
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ProcessingResult:
    \"\"\"Result of data processing operation.\"\"\"
    success: bool
    count: int
    output_path: Optional[Path] = None
    errors: List[str] = field(default_factory=list)

class DataProcessor:
    \"\"\"Handles JSON data processing with validation and file output.\"\"\"

    def __init__(self, output_dir: Path = Path("./output")):
        \"\"\"Initialize processor with output directory.

        Args:
            output_dir: Directory for processed data files
        \"\"\"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def process_json_data(
        self,
        json_data: str,
        filename: Optional[str] = None
    ) -> ProcessingResult:
        \"\"\"Process JSON data and optionally save to file.

        Args:
            json_data: JSON string to process
            filename: Optional filename for output

        Returns:
            ProcessingResult with operation details

        Raises:
            json.JSONDecodeError: If data is not valid JSON
            IOError: If file operations fail
        \"\"\"
        result = ProcessingResult(success=False, count=0)

        try:
            # Parse JSON data
            data = json.loads(json_data)

            # Process data (ensure it's a list)
            if not isinstance(data, list):
                data = [data]

            # Validate and process each item
            processed_data = []
            for item in data:
                if self._validate_item(item):
                    processed_data.append(self._process_item(item))
                else:
                    result.errors.append(f"Invalid item: {item}")

            # Save to file if filename provided
            if filename:
                output_path = self.output_dir / filename
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        "processed": processed_data,
                        "count": len(processed_data),
                        "timestamp": str(Path.cwd())
                    }, f, indent=2, ensure_ascii=False)
                result.output_path = output_path

            result.success = len(result.errors) == 0
            result.count = len(processed_data)

        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON data: {e.msg}"
            logger.error(error_msg)
            result.errors.append(error_msg)
        except IOError as e:
            error_msg = f"File operation failed: {e}"
            logger.error(error_msg)
            result.errors.append(error_msg)

        return result

    def _validate_item(self, item: Any) -> bool:
        \"\"\"Validate a single data item.\"\"\"
        return isinstance(item, dict) and "id" in item

    def _process_item(self, item: Any) -> Dict[str, Any]:
        \"\"\"Process a single validated item.\"\"\"
        return {
            "id": item["id"],
            "processed": True,
            "timestamp": Path.cwd().strftime("%Y-%m-%d %H:%M:%S")
        }"""

    def _get_python_architect_example(self) -> str:
        """Get Python architecture example."""
        return """# File: src/data_pipeline/__init__.py
# [NEW] or [MODIFIED]

\"\"\"
Data Pipeline Architecture Module

This module provides a scalable architecture for processing
large volumes of JSON data with the following design principles:

- Single Responsibility: Each component has one clear purpose
- Dependency Injection: Components receive dependencies via constructor
- Async Support: All I/O operations are async-compatible
- Error Handling: Comprehensive error handling with proper logging
- Testing: Fully testable with mocked dependencies
\"\"\"

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable
from pathlib import Path
import asyncio
from dataclasses import dataclass

# Core Interfaces
@runtime_checkable
class DataSource(Protocol):
    \"\"\"Protocol for data source implementations.\"\"\"

    async def read_data(self) -> str:
        \"\"\"Read data from source.\"\"\"
        ...

    async def write_data(self, data: str) -> None:
        \"\"\"Write processed data back to source.\"\"\"
        ...

@runtime_checkable
class DataProcessor(Protocol):
    \"\"\"Protocol for data processing implementations.\"\"\"

    async def process(self, data: str) -> str:
        \"\"\"Process data and return results.\"\"\"
        ...

# Configuration
@dataclass
class PipelineConfig:
    \"\"\"Configuration for data pipeline.\"\"\"
    input_path: Path
    output_path: Path
    chunk_size: int = 1000
    max_workers: int = 4
    retry_attempts: int = 3

# Core Components
class DataPipeline:
    \"\"\"Main pipeline orchestrator with dependency injection.\"\"\"

    def __init__(
        self,
        config: PipelineConfig,
        data_source: DataSource,
        processor: DataProcessor
    ):
        self.config = config
        self.data_source = data_source
        self.processor = processor

    async def run(self) -> Dict[str, Any]:
        \"\"\"Execute the complete data pipeline.\"\"\"
        try:
            # Read data in chunks
            raw_data = await self.data_source.read_data()

            # Process data in parallel chunks
            processed_chunks = await self._process_in_chunks(raw_data)

            # Write results
            result_data = "\\n".join(processed_chunks)
            await self.data_source.write_data(result_data)

            return {
                "status": "success",
                "chunks_processed": len(processed_chunks),
                "output_path": str(self.config.output_path)
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "chunks_processed": 0
            }

    async def _process_in_chunks(self, data: str) -> List[str]:
        \"\"\"Process data in parallel chunks.\"\"\"
        # Implementation would use asyncio for parallel processing
        # This is a simplified example
        return [await self.processor.process(data)]

# Factory Functions
def create_file_pipeline(config: PipelineConfig) -> DataPipeline:
    \"\"\"Factory function for file-based pipeline.\"\"\"
    return DataPipeline(
        config=config,
        data_source=FileDataSource(config),
        processor=JsonDataProcessor()
    )

# Example Usage
async def main():
    config = PipelineConfig(
        input_path=Path("input/data.json"),
        output_path=Path("output/processed.json")
    )

    pipeline = create_file_pipeline(config)
    result = await pipeline.run()

    print(f"Pipeline completed: {result}")

if __name__ == "__main__":
    asyncio.run(main())"""

    def _get_python_peer_example(self) -> str:
        """Get Python peer review example."""
        return """# File: services/user_service.py
# [REVIEW] Peer Review Comments

from typing import Optional, Dict, Any
from datetime import datetime
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class UserService:
    \"\"\"Service for user management operations.\"\"\"

    def __init__(self, db_connection: str, cache_client=None):
        \"\"\"Initialize UserService.

        Args:
            db_connection: Database connection string
            cache_client: Optional cache client for performance
        \"\"\"
        self.db_connection = db_connection
        self.cache_client = cache_client

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        \"\"\"Retrieve user by ID with caching.

        Args:
            user_id: Unique user identifier

        Returns:
            User data dictionary or None if not found

        Raises:
            DatabaseError: If database operation fails
        \"\"\"
        # Check cache first
        cache_key = f"user:{user_id}"
        if self.cache_client:
            cached_data = self.cache_client.get(cache_key)
            if cached_data:
                logger.info(f"Cache hit for user {user_id}")
                return cached_data

        # Fetch from database
        try:
            user_data = self._fetch_user_from_db(user_id)
            if user_data:
                # Cache the result
                if self.cache_client:
                    self.cache_client.setex(cache_key, 300, user_data)  # 5 min TTL
                return user_data
        except Exception as e:
            logger.error(f"Failed to fetch user {user_id}: {e}")
            raise DatabaseError(f"User fetch failed: {e}")

        return None

    def _fetch_user_from_db(self, user_id: int) -> Optional[Dict[str, Any]]:
        \"\"\"Fetch user data from database.\"\"\"
        # Database implementation would go here
        # This is a placeholder for the actual DB query
        pass

# Peer Review Comments:
# =====================

# ✅ GOOD:
# - Proper type hints throughout
# - Good docstring with Args/Returns/Raises
# - Appropriate error handling and logging
# - Cache optimization for performance
# - Single responsibility principle

# ⚠️  NEEDS IMPROVEMENT:
# 1. Missing import for DatabaseError - should be imported or defined
# 2. No input validation for user_id parameter
# 3. Cache TTL of 300 seconds may be too short for user data
# 4. No handling of potential cache client failures

# 🔧 SUGGESTED CHANGES:
# - Add validation: if not isinstance(user_id, int) or user_id <= 0:
# - Import DatabaseError or define custom exception
# - Consider longer cache TTL or make it configurable
# - Add try-catch around cache operations
# - Add unit tests for cache hit/miss scenarios

# 📝 GENERAL ADVICE:
# - Consider using dataclasses for user data structure
# - Add metrics/monitoring for cache hit rates
# - Consider connection pooling for database operations
# - Add integration tests for the complete flow"""

    def _get_python_sdet_example(self) -> str:
        """Get Python SDET example."""
        return """# File: tests/test_data_processor.py
# [NEW] or [MODIFIED]

\"\"\"
Comprehensive test suite for DataProcessor class.

This module demonstrates best practices for Python testing:
- pytest framework with fixtures
- Comprehensive test coverage
- Mocking external dependencies
- Testing edge cases and error conditions
\"\"\"

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_processor import DataProcessor, ProcessingResult, DatabaseError


class TestDataProcessor:
    \"\"\"Test suite for DataProcessor functionality.\"\"\"

    @pytest.fixture
    def temp_dir(self):
        \"\"\"Create temporary directory for test outputs.\"\"\"
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def processor(self, temp_dir):
        \"\"\"Create DataProcessor instance for testing.\"\"\"
        return DataProcessor(output_dir=temp_dir)

    @pytest.fixture
    def sample_json_data(self):
        \"\"\"Sample JSON data for testing.\"\"\"
        return json.dumps([
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"}
        ])

    @pytest.fixture
    def invalid_json_data(self):
        \"\"\"Invalid JSON for error testing.\"\"\"
        return '{"invalid": json}'

    def test_process_valid_json_data(self, processor, temp_dir, sample_json_data):
        \"\"\"Test processing valid JSON data.\"\"\"
        result = processor.process_json_data(sample_json_data, "test_output.json")

        # Verify result
        assert result.success is True
        assert result.count == 2
        assert result.errors == []
        assert result.output_path == temp_dir / "test_output.json"

        # Verify file was created and contains expected data
        assert result.output_path.exists()
        with open(result.output_path, 'r') as f:
            saved_data = json.load(f)
            assert saved_data["count"] == 2
            assert saved_data["processed"] == True
            assert len(saved_data["data"]) == 2

    def test_process_json_without_filename(self, processor, sample_json_data):
        \"\"\"Test processing JSON data without saving to file.\"\"\"
        result = processor.process_json_data(sample_json_data)

        assert result.success is True
        assert result.count == 2
        assert result.output_path is None

    def test_process_invalid_json_raises_error(self, processor, invalid_json_data):
        \"\"\"Test that invalid JSON raises appropriate error.\"\"\"
        with pytest.raises(json.JSONDecodeError):
            processor.process_json_data(invalid_json_data)

    def test_process_empty_array(self, processor):
        \"\"\"Test processing empty JSON array.\"\"\"
        empty_data = json.dumps([])
        result = processor.process_json_data(empty_data)

        assert result.success is True
        assert result.count == 0

    def test_process_invalid_item_structure(self, processor):
        \"\"\"Test processing data with invalid item structure.\"\"\"
        invalid_data = json.dumps([
            {"name": "Alice"},  # Missing 'id' field
            {"id": 2, "name": "Bob"}
        ])

        result = processor.process_json_data(invalid_data)

        # Should process valid items only
        assert result.success is True
        assert result.count == 1  # Only Bob has valid structure
        assert len(result.errors) == 1
        assert "Invalid item" in result.errors[0]

    @patch('data_processor.json.loads')
    def test_json_decode_error_handling(self, mock_json_loads, processor):
        \"\"\"Test handling of JSON decode errors.\"\"\"
        mock_json_loads.side_effect = json.JSONDecodeError("Invalid JSON", "doc", 0)

        with pytest.raises(json.JSONDecodeError) as exc_info:
            processor.process_json_data('{"invalid": json}')

        assert "Invalid JSON data" in str(exc_info.value)

    def test_file_operation_error_handling(self, temp_dir, sample_json_data):
        \"\"\"Test handling of file operation errors.\"\"\"
        # Create processor with read-only directory
        readonly_dir = temp_dir / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)  # Read-only

        processor = DataProcessor(output_dir=readonly_dir)

        # Should raise IOError when trying to write
        with pytest.raises(IOError) as exc_info:
            processor.process_json_data(sample_json_data, "test.json")

        assert "File operation failed" in str(exc_info.value)

    @pytest.mark.parametrize("test_data,expected_count", [
        ([{"id": 1}], 1),
        ([{"id": 1}, {"id": 2}, {"id": 3}], 3),
        ([], 0),
    ])
    def test_process_different_data_sizes(self, processor, test_data, expected_count):
        \"\"\"Test processing different data sizes.\"\"\"
        json_data = json.dumps(test_data)
        result = processor.process_json_data(json_data)

        assert result.success is True
        assert result.count == expected_count

    @pytest.mark.integration
    def test_full_processing_workflow(self, processor, temp_dir, sample_json_data):
        \"\"\"Integration test for complete processing workflow.\"\"\"
        # Process data
        result = processor.process_json_data(sample_json_data, "integration_test.json")

        # Verify complete workflow
        assert result.success is True
        assert result.count == 2
        assert result.output_path.exists()

        # Verify file structure
        with open(result.output_path, 'r') as f:
            data = json.load(f)
            assert "processed" in data
            assert "count" in data
            assert "data" in data
            assert "timestamp" in data

    def test_processor_initialization(self, temp_dir):
        \"\"\"Test DataProcessor initialization.\"\"\"
        processor = DataProcessor(output_dir=temp_dir)

        assert processor.output_dir == temp_dir
        assert processor.output_dir.exists()

    @pytest.mark.performance
    def test_large_dataset_performance(self, processor, temp_dir):
        \"\"\"Test performance with large dataset.\"\"\"
        # Generate large dataset
        large_data = [{"id": i, "name": f"User{i}"} for i in range(1000)]
        json_data = json.dumps(large_data)

        import time
        start_time = time.time()

        result = processor.process_json_data(json_data, "performance_test.json")

        processing_time = time.time() - start_time

        assert result.success is True
        assert result.count == 1000
        assert processing_time < 5.0  # Should process within 5 seconds
        assert result.output_path.exists()

# Test configuration
pytest_plugins = [
    "pytest_asyncio",
    "pytest_cov",
]

# Coverage configuration
def pytest_configure(config):
    \"\"\"Configure pytest for coverage reporting.\"\"\"
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "performance: mark test as performance test")
    config.addinivalue_line("markers", "unit: mark test as unit test")

# Test discovery patterns
collect_ignore = ["setup.py"]

# Test output configuration
def pytest_collection_modifyitems(config, items):
    \"\"\"Modify test collection for better organization.\"\"\"
    for item in items:
        # Add markers based on test function names
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif "performance" in item.nodeid:
            item.add_marker(pytest.mark.performance)
        else:
            item.add_marker(pytest.mark.unit)"""