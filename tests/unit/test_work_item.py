"""Unit tests for WorkItem model."""

import pytest
from vivek.domain.models.work_item import WorkItem, ExecutionMode


class TestWorkItemCreation:
    """Test WorkItem creation and initialization."""

    def test_create_valid_work_item(self):
        """Test creating a valid work item with required fields."""
        item = WorkItem(
            id="item_1",
            file_path="src/module.py",
            description="Create module",
            mode=ExecutionMode.CODER
        )

        assert item.id == "item_1"
        assert item.file_path == "src/module.py"
        assert item.description == "Create module"
        assert item.mode == ExecutionMode.CODER
        assert item.language == "python"
        assert item.file_status == "new"
        assert item.dependencies == []
        assert item.context is None

    def test_create_work_item_with_all_fields(self):
        """Test creating a work item with all fields specified."""
        item = WorkItem(
            id="item_2",
            file_path="tests/test_module.py",
            description="Create test module",
            mode=ExecutionMode.SDET,
            language="python",
            file_status="existing",
            dependencies=["item_1"],
            context="Additional context for execution"
        )

        assert item.id == "item_2"
        assert item.file_path == "tests/test_module.py"
        assert item.description == "Create test module"
        assert item.mode == ExecutionMode.SDET
        assert item.language == "python"
        assert item.file_status == "existing"
        assert item.dependencies == ["item_1"]
        assert item.context == "Additional context for execution"

    def test_create_work_item_with_multiple_dependencies(self):
        """Test creating a work item with multiple dependencies."""
        dependencies = ["item_1", "item_2", "item_3"]
        item = WorkItem(
            id="item_4",
            file_path="src/complex_module.py",
            description="Complex implementation",
            mode=ExecutionMode.CODER,
            dependencies=dependencies
        )

        assert item.dependencies == dependencies
        assert len(item.dependencies) == 3

    def test_work_item_default_language_is_python(self):
        """Test that default language is python."""
        item = WorkItem(
            id="item_1",
            file_path="src/module.py",
            description="Test",
            mode=ExecutionMode.CODER
        )

        assert item.language == "python"

    def test_work_item_default_file_status_is_new(self):
        """Test that default file_status is 'new'."""
        item = WorkItem(
            id="item_1",
            file_path="src/module.py",
            description="Test",
            mode=ExecutionMode.CODER
        )

        assert item.file_status == "new"

    def test_work_item_default_dependencies_is_empty(self):
        """Test that default dependencies list is empty."""
        item = WorkItem(
            id="item_1",
            file_path="src/module.py",
            description="Test",
            mode=ExecutionMode.CODER
        )

        assert item.dependencies == []

    def test_work_item_default_context_is_none(self):
        """Test that default context is None."""
        item = WorkItem(
            id="item_1",
            file_path="src/module.py",
            description="Test",
            mode=ExecutionMode.CODER
        )

        assert item.context is None


class TestWorkItemValidation:
    """Test WorkItem validation in __post_init__."""

    def test_empty_id_raises_value_error(self):
        """Test that empty ID raises ValueError."""
        with pytest.raises(ValueError, match="Work item ID cannot be empty"):
            WorkItem(
                id="",
                file_path="src/module.py",
                description="Test",
                mode=ExecutionMode.CODER
            )

    def test_empty_file_path_raises_value_error(self):
        """Test that empty file_path raises ValueError."""
        with pytest.raises(ValueError, match="File path cannot be empty"):
            WorkItem(
                id="item_1",
                file_path="",
                description="Test",
                mode=ExecutionMode.CODER
            )

    def test_empty_description_raises_value_error(self):
        """Test that empty description raises ValueError."""
        with pytest.raises(ValueError, match="Description cannot be empty"):
            WorkItem(
                id="item_1",
                file_path="src/module.py",
                description="",
                mode=ExecutionMode.CODER
            )

    def test_invalid_file_status_raises_value_error(self):
        """Test that invalid file_status raises ValueError."""
        with pytest.raises(ValueError, match="Invalid file_status"):
            WorkItem(
                id="item_1",
                file_path="src/module.py",
                description="Test",
                mode=ExecutionMode.CODER,
                file_status="invalid"
            )

    def test_valid_file_status_new(self):
        """Test that file_status 'new' is valid."""
        item = WorkItem(
            id="item_1",
            file_path="src/module.py",
            description="Test",
            mode=ExecutionMode.CODER,
            file_status="new"
        )

        assert item.file_status == "new"

    def test_valid_file_status_existing(self):
        """Test that file_status 'existing' is valid."""
        item = WorkItem(
            id="item_1",
            file_path="src/module.py",
            description="Test",
            mode=ExecutionMode.CODER,
            file_status="existing"
        )

        assert item.file_status == "existing"




class TestExecutionMode:
    """Test ExecutionMode enum."""

    def test_execution_mode_coder(self):
        """Test CODER execution mode."""
        assert ExecutionMode.CODER == "coder"
        assert ExecutionMode.CODER.value == "coder"

    def test_execution_mode_sdet(self):
        """Test SDET execution mode."""
        assert ExecutionMode.SDET == "sdet"
        assert ExecutionMode.SDET.value == "sdet"

    def test_execution_mode_is_string_enum(self):
        """Test that ExecutionMode is a string enum."""
        mode = ExecutionMode.CODER
        assert isinstance(mode, str)
        assert mode.value == "coder"

    def test_execution_mode_from_string(self):
        """Test creating ExecutionMode from string."""
        mode = ExecutionMode("coder")
        assert mode == ExecutionMode.CODER

    def test_invalid_execution_mode_raises_error(self):
        """Test that invalid execution mode raises error."""
        with pytest.raises(ValueError):
            ExecutionMode("invalid")


class TestWorkItemEdgeCases:
    """Test edge cases for WorkItem."""

    def test_work_item_with_long_description(self):
        """Test creating work item with very long description."""
        long_desc = "x" * 10000
        item = WorkItem(
            id="item_1",
            file_path="src/module.py",
            description=long_desc,
            mode=ExecutionMode.CODER
        )

        assert item.description == long_desc

    def test_work_item_with_special_characters_in_fields(self):
        """Test work item with special characters in fields."""
        item = WorkItem(
            id="item_!@#$%",
            file_path="src/module-file_name.py",
            description="Test with special chars: @#$%^&*()",
            mode=ExecutionMode.CODER
        )

        assert item.id == "item_!@#$%"
        assert item.file_path == "src/module-file_name.py"
        assert item.description == "Test with special chars: @#$%^&*()"

    def test_work_item_with_nested_path(self):
        """Test work item with deeply nested file path."""
        path = "src/deeply/nested/path/to/module.py"
        item = WorkItem(
            id="item_1",
            file_path=path,
            description="Test",
            mode=ExecutionMode.CODER
        )

        assert item.file_path == path

    def test_work_item_with_many_dependencies(self):
        """Test work item with many dependencies."""
        dependencies = [f"item_{i}" for i in range(100)]
        item = WorkItem(
            id="item_main",
            file_path="src/module.py",
            description="Test",
            mode=ExecutionMode.CODER,
            dependencies=dependencies
        )

        assert len(item.dependencies) == 100
        assert item.dependencies == dependencies

    def test_work_item_with_empty_context(self):
        """Test work item with empty context string."""
        item = WorkItem(
            id="item_1",
            file_path="src/module.py",
            description="Test",
            mode=ExecutionMode.CODER,
            context=""
        )

        assert item.context == ""

    def test_work_item_with_whitespace_only_fields(self):
        """Test that whitespace-only fields are treated as valid (not empty)."""
        item = WorkItem(
            id="   ",
            file_path="src/module.py",
            description="Test",
            mode=ExecutionMode.CODER
        )

        assert item.id == "   "

    def test_different_languages(self):
        """Test work item with different programming languages."""
        languages = ["python", "typescript", "go", "java", "javascript"]
        
        for lang in languages:
            item = WorkItem(
                id="item_1",
                file_path=f"src/module.{lang}",
                description="Test",
                mode=ExecutionMode.CODER,
                language=lang
            )
            assert item.language == lang


class TestWorkItemImmutability:
    """Test WorkItem immutability (dataclass behavior)."""

    def test_work_item_is_dataclass(self):
        """Test that WorkItem is a dataclass."""
        item = WorkItem(
            id="item_1",
            file_path="src/module.py",
            description="Test",
            mode=ExecutionMode.CODER
        )

        # Dataclasses should have __dataclass_fields__
        assert hasattr(item, "__dataclass_fields__")

    def test_work_item_fields_can_be_modified(self):
        """Test that WorkItem fields can be modified after creation."""
        item = WorkItem(
            id="item_1",
            file_path="src/module.py",
            description="Test",
            mode=ExecutionMode.CODER
        )

        item.description = "Updated description"
        assert item.description == "Updated description"

    def test_dependencies_list_modification(self):
        """Test that dependencies list can be modified."""
        item = WorkItem(
            id="item_1",
            file_path="src/module.py",
            description="Test",
            mode=ExecutionMode.CODER,
            dependencies=["item_0"]
        )

        item.dependencies.append("item_2")
        assert len(item.dependencies) == 2
        assert "item_2" in item.dependencies


class TestWorkItemEquality:
    """Test WorkItem equality comparison."""

    def test_two_work_items_with_same_data_are_equal(self):
        """Test that two work items with same data are equal."""
        item1 = WorkItem(
            id="item_1",
            file_path="src/module.py",
            description="Test",
            mode=ExecutionMode.CODER
        )
        item2 = WorkItem(
            id="item_1",
            file_path="src/module.py",
            description="Test",
            mode=ExecutionMode.CODER
        )

        assert item1 == item2

    def test_two_work_items_with_different_ids_are_not_equal(self):
        """Test that work items with different IDs are not equal."""
        item1 = WorkItem(
            id="item_1",
            file_path="src/module.py",
            description="Test",
            mode=ExecutionMode.CODER
        )
        item2 = WorkItem(
            id="item_2",
            file_path="src/module.py",
            description="Test",
            mode=ExecutionMode.CODER
        )

        assert item1 != item2

    def test_two_work_items_with_different_descriptions_are_not_equal(self):
        """Test that work items with different descriptions are not equal."""
        item1 = WorkItem(
            id="item_1",
            file_path="src/module.py",
            description="Test 1",
            mode=ExecutionMode.CODER
        )
        item2 = WorkItem(
            id="item_1",
            file_path="src/module.py",
            description="Test 2",
            mode=ExecutionMode.CODER
        )

        assert item1 != item2
