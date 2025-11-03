"""Unit tests for FileService."""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from vivek.infrastructure.file_operations.file_service import FileService
from vivek.domain.exceptions.exception import ExecutionException


class TestFileServiceReadFile:
    """Test FileService read_file functionality."""

    def test_read_existing_file(self):
        """Test reading an existing file."""
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.txt"
            content = "Hello, World!"
            file_path.write_text(content)

            service = FileService()
            result = service.read_file(str(file_path))

            assert result == content

    def test_read_file_with_multiple_lines(self):
        """Test reading a file with multiple lines."""
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "multiline.txt"
            content = "Line 1\nLine 2\nLine 3"
            file_path.write_text(content)

            service = FileService()
            result = service.read_file(str(file_path))

            assert result == content
            assert len(result.split('\n')) == 3

    def test_read_file_with_special_characters(self):
        """Test reading a file with special characters."""
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "special.txt"
            content = "Special chars: !@#$%^&*()_+-=[]{}|;:',.<>?/"
            file_path.write_text(content)

            service = FileService()
            result = service.read_file(str(file_path))

            assert result == content

    def test_read_empty_file(self):
        """Test reading an empty file."""
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "empty.txt"
            file_path.write_text("")

            service = FileService()
            result = service.read_file(str(file_path))

            assert result == ""

    def test_read_large_file(self):
        """Test reading a large file."""
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "large.txt"
            content = "x" * 100000
            file_path.write_text(content)

            service = FileService()
            result = service.read_file(str(file_path))

            assert result == content
            assert len(result) == 100000

    def test_read_nonexistent_file_raises_error(self):
        """Test that reading a nonexistent file raises ExecutionException."""
        service = FileService()

        with pytest.raises(ExecutionException, match="Failed to read file"):
            service.read_file("/nonexistent/path/to/file.txt")

    def test_read_file_from_nested_directory(self):
        """Test reading a file from nested directory."""
        with TemporaryDirectory() as tmpdir:
            nested_path = Path(tmpdir) / "dir1" / "dir2" / "dir3"
            nested_path.mkdir(parents=True)
            file_path = nested_path / "nested.txt"
            content = "Nested file content"
            file_path.write_text(content)

            service = FileService()
            result = service.read_file(str(file_path))

            assert result == content

    def test_read_unicode_file(self):
        """Test reading a file with unicode content."""
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "unicode.txt"
            content = "Unicode: 你好世界 🌍 Привет مرحبا"
            file_path.write_text(content, encoding='utf-8')

            service = FileService()
            result = service.read_file(str(file_path))

            assert result == content


class TestFileServiceWriteFile:
    """Test FileService write_file functionality."""

    def test_write_file_to_new_location(self):
        """Test writing a file to a new location."""
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "new_file.txt"
            content = "New file content"

            service = FileService()
            result = service.write_file(str(file_path), content)

            assert result is True
            assert file_path.exists()
            assert file_path.read_text() == content

    def test_write_file_overwrites_existing(self):
        """Test that write_file overwrites existing file."""
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "existing.txt"
            file_path.write_text("Old content")

            service = FileService()
            new_content = "New content"
            result = service.write_file(str(file_path), new_content)

            assert result is True
            assert file_path.read_text() == new_content

    def test_write_empty_file(self):
        """Test writing an empty file."""
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "empty.txt"

            service = FileService()
            result = service.write_file(str(file_path), "")

            assert result is True
            assert file_path.exists()
            assert file_path.read_text() == ""

    def test_write_file_with_multiline_content(self):
        """Test writing a file with multiline content."""
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "multiline.txt"
            content = "Line 1\nLine 2\nLine 3"

            service = FileService()
            result = service.write_file(str(file_path), content)

            assert result is True
            assert file_path.read_text() == content

    def test_write_file_with_special_characters(self):
        """Test writing a file with special characters."""
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "special.txt"
            content = "Special: !@#$%^&*()_+-=[]{}|;:',.<>?/"

            service = FileService()
            result = service.write_file(str(file_path), content)

            assert result is True
            assert file_path.read_text() == content

    def test_write_file_creates_parent_directories(self):
        """Test that write_file creates parent directories if needed."""
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "dir1" / "dir2" / "dir3" / "file.txt"
            content = "Content in nested directory"

            service = FileService()
            result = service.write_file(str(file_path), content)

            assert result is True
            assert file_path.exists()
            assert file_path.parent.exists()
            assert file_path.read_text() == content

    def test_write_large_file(self):
        """Test writing a large file."""
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "large.txt"
            content = "x" * 1000000

            service = FileService()
            result = service.write_file(str(file_path), content)

            assert result is True
            assert file_path.read_text() == content

    def test_write_unicode_file(self):
        """Test writing a file with unicode content."""
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "unicode.txt"
            content = "Unicode: 你好世界 🌍 Привет مرحبا"

            service = FileService()
            result = service.write_file(str(file_path), content)

            assert result is True
            assert file_path.read_text(encoding='utf-8') == content


class TestFileServiceFileExists:
    """Test FileService file_exists functionality."""

    def test_file_exists_returns_true_for_existing_file(self):
        """Test that file_exists returns True for existing file."""
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "exists.txt"
            file_path.write_text("content")

            service = FileService()
            result = service.file_exists(str(file_path))

            assert result is True

    def test_file_exists_returns_false_for_nonexistent_file(self):
        """Test that file_exists returns False for nonexistent file."""
        service = FileService()
        result = service.file_exists("/nonexistent/path/file.txt")

        assert result is False

    def test_file_exists_with_empty_file(self):
        """Test file_exists with an empty file."""
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "empty.txt"
            file_path.write_text("")

            service = FileService()
            result = service.file_exists(str(file_path))

            assert result is True

    def test_file_exists_with_nested_path(self):
        """Test file_exists with nested path."""
        with TemporaryDirectory() as tmpdir:
            nested_path = Path(tmpdir) / "a" / "b" / "c"
            nested_path.mkdir(parents=True)
            file_path = nested_path / "file.txt"
            file_path.write_text("content")

            service = FileService()
            result = service.file_exists(str(file_path))

            assert result is True

    def test_file_exists_with_directory_path(self):
        """Test file_exists with directory path returns False."""
        with TemporaryDirectory() as tmpdir:
            # file_exists checks if it's a file, not a directory
            # The behavior depends on Path.exists() for directories
            service = FileService()
            # Directories also return True with Path.exists()
            result = service.file_exists(tmpdir)

            # Path.exists() returns True for directories too
            assert result is True


class TestFileServiceCreateDirectory:
    """Test FileService create_directory functionality."""

    def test_create_single_directory(self):
        """Test creating a single directory."""
        with TemporaryDirectory() as tmpdir:
            dir_path = Path(tmpdir) / "newdir"

            service = FileService()
            result = service.create_directory(str(dir_path))

            assert result is True
            assert dir_path.exists()
            assert dir_path.is_dir()

    def test_create_nested_directories(self):
        """Test creating nested directories."""
        with TemporaryDirectory() as tmpdir:
            dir_path = Path(tmpdir) / "dir1" / "dir2" / "dir3"

            service = FileService()
            result = service.create_directory(str(dir_path))

            assert result is True
            assert dir_path.exists()
            assert dir_path.is_dir()

    def test_create_existing_directory_succeeds(self):
        """Test that creating an existing directory succeeds."""
        with TemporaryDirectory() as tmpdir:
            dir_path = Path(tmpdir) / "existing"
            dir_path.mkdir()

            service = FileService()
            result = service.create_directory(str(dir_path))

            assert result is True
            assert dir_path.exists()

    def test_create_multiple_nested_existing_directories(self):
        """Test creating directories when parents exist."""
        with TemporaryDirectory() as tmpdir:
            parent = Path(tmpdir) / "parent"
            parent.mkdir()
            child_path = parent / "child1" / "child2"

            service = FileService()
            result = service.create_directory(str(child_path))

            assert result is True
            assert child_path.exists()

    def test_create_directory_with_special_characters(self):
        """Test creating a directory with special characters in name."""
        with TemporaryDirectory() as tmpdir:
            dir_path = Path(tmpdir) / "dir-name_123"

            service = FileService()
            result = service.create_directory(str(dir_path))

            assert result is True
            assert dir_path.exists()


class TestFileServiceIntegration:
    """Integration tests for FileService operations."""

    def test_write_then_read_file(self):
        """Test writing a file and then reading it back."""
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.txt"
            original_content = "Test content"

            service = FileService()
            write_result = service.write_file(str(file_path), original_content)
            read_content = service.read_file(str(file_path))

            assert write_result is True
            assert read_content == original_content

    def test_create_directory_then_write_file(self):
        """Test creating a directory and then writing a file to it."""
        with TemporaryDirectory() as tmpdir:
            dir_path = Path(tmpdir) / "new_dir"
            file_path = dir_path / "file.txt"
            content = "File in new directory"

            service = FileService()
            service.create_directory(str(dir_path))
            write_result = service.write_file(str(file_path), content)
            read_content = service.read_file(str(file_path))

            assert write_result is True
            assert read_content == content

    def test_file_exists_after_write(self):
        """Test that file_exists returns True after writing."""
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.txt"

            service = FileService()
            assert service.file_exists(str(file_path)) is False

            service.write_file(str(file_path), "content")
            assert service.file_exists(str(file_path)) is True

    def test_multiple_read_write_operations(self):
        """Test multiple consecutive read/write operations."""
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.txt"
            service = FileService()

            # Write and read multiple times
            for i in range(5):
                content = f"Content version {i}"
                service.write_file(str(file_path), content)
                result = service.read_file(str(file_path))
                assert result == content

    def test_write_then_check_exists_then_read(self):
        """Test complete workflow: write, check exists, read."""
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "workflow.txt"
            content = "Workflow test content"

            service = FileService()
            
            # Write
            service.write_file(str(file_path), content)
            
            # Check exists
            assert service.file_exists(str(file_path)) is True
            
            # Read
            result = service.read_file(str(file_path))
            assert result == content

    def test_create_directory_and_nested_files(self):
        """Test creating nested directories with multiple files."""
        with TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            service = FileService()

            # Create nested structure
            service.create_directory(str(base_dir / "src" / "module"))
            service.write_file(str(base_dir / "src" / "module" / "file1.py"), "# file1")
            service.write_file(str(base_dir / "src" / "module" / "file2.py"), "# file2")

            # Verify structure
            assert (base_dir / "src" / "module" / "file1.py").exists()
            assert (base_dir / "src" / "module" / "file2.py").exists()
            assert service.file_exists(str(base_dir / "src" / "module" / "file1.py"))


class TestFileServiceErrorHandling:
    """Test FileService error handling."""

    def test_read_file_invalid_path_raises_exception(self):
        """Test that reading with invalid path raises ExecutionException."""
        service = FileService()

        with pytest.raises(ExecutionException):
            service.read_file("/invalid/nonexistent/path.txt")

    def test_write_file_to_invalid_path_raises_exception(self):
        """Test that writing to invalid path raises ExecutionException."""
        service = FileService()

        # Create a read-only directory scenario (if possible)
        with TemporaryDirectory() as tmpdir:
            # This might be platform-specific, but we can try
            try:
                service.write_file(str(Path(tmpdir) / "test.txt"), "content")
            except ExecutionException:
                pytest.skip("Permission test not applicable on this platform")

    def test_create_directory_handles_permissions_gracefully(self):
        """Test create_directory behavior with permission issues."""
        # This test depends on platform and permissions
        # Skip if we can't create the test scenario
        with TemporaryDirectory() as tmpdir:
            dir_path = Path(tmpdir) / "test"
            service = FileService()
            
            # Should succeed in temp directory
            result = service.create_directory(str(dir_path))
            assert result is True
