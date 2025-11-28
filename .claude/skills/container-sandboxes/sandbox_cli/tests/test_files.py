"""
Unit tests for file operations (files.py).
"""

import pytest
from pathlib import Path
from src.modules import files as files_module


@pytest.mark.requires_images
class TestListFiles:
    """Test file listing functionality."""

    def test_list_root_directory(self, sandbox):
        """Test listing files in root directory."""
        files = files_module.list_files(sandbox.sandbox_id, "/")

        assert isinstance(files, list)
        assert len(files) > 0

        # Should have standard directories
        names = [f["name"] for f in files]
        assert "home" in names or "usr" in names

    def test_list_home_directory(self, sandbox):
        """Test listing files in /home/user directory."""
        files = files_module.list_files(sandbox.sandbox_id, "/home/user")

        assert isinstance(files, list)
        # May be empty or have default files

    def test_list_nonexistent_directory(self, sandbox):
        """Test listing a non-existent directory raises error."""
        with pytest.raises(FileNotFoundError):
            files_module.list_files(sandbox.sandbox_id, "/nonexistent")

    def test_file_info_structure(self, sandbox):
        """Test that file info has expected structure."""
        files = files_module.list_files(sandbox.sandbox_id, "/home/user")

        if len(files) > 0:
            file_info = files[0]
            assert "name" in file_info
            assert "path" in file_info
            assert "type" in file_info
            assert "size" in file_info
            assert "permissions" in file_info
            assert file_info["type"] in ["file", "dir"]


@pytest.mark.requires_images
class TestReadWriteFiles:
    """Test reading and writing files."""

    def test_write_and_read_text_file(self, sandbox):
        """Test writing and reading a text file."""
        content = "Hello, world!\nThis is a test."
        path = "/home/user/test.txt"

        # Write file
        result = files_module.write_file(sandbox.sandbox_id, path, content)
        assert result["path"] == path

        # Read file back
        read_content = files_module.read_file(sandbox.sandbox_id, path)
        assert read_content == content

    def test_write_empty_file(self, sandbox):
        """Test writing an empty file."""
        path = "/home/user/empty.txt"

        files_module.write_file(sandbox.sandbox_id, path, "")

        content = files_module.read_file(sandbox.sandbox_id, path)
        assert content == ""

    def test_write_file_with_special_characters(self, sandbox):
        """Test writing a file with special characters."""
        content = "Line with 'quotes' and \"double quotes\" and $variables"
        path = "/home/user/special.txt"

        files_module.write_file(sandbox.sandbox_id, path, content)

        read_content = files_module.read_file(sandbox.sandbox_id, path)
        assert read_content == content

    def test_write_multiline_file(self, sandbox):
        """Test writing a multi-line file."""
        content = "Line 1\nLine 2\nLine 3\n"
        path = "/home/user/multiline.txt"

        files_module.write_file(sandbox.sandbox_id, path, content)

        read_content = files_module.read_file(sandbox.sandbox_id, path)
        assert read_content == content

    def test_overwrite_existing_file(self, sandbox):
        """Test overwriting an existing file."""
        path = "/home/user/overwrite.txt"

        # Write initial content
        files_module.write_file(sandbox.sandbox_id, path, "initial")

        # Overwrite
        files_module.write_file(sandbox.sandbox_id, path, "overwritten")

        # Read and verify
        content = files_module.read_file(sandbox.sandbox_id, path)
        assert content == "overwritten"

    def test_read_nonexistent_file(self, sandbox):
        """Test reading a non-existent file raises error."""
        with pytest.raises(FileNotFoundError):
            files_module.read_file(sandbox.sandbox_id, "/nonexistent/file.txt")


@pytest.mark.requires_images
class TestBinaryFiles:
    """Test binary file operations."""

    def test_write_and_read_binary_file(self, sandbox):
        """Test writing and reading a binary file."""
        data = bytes([0, 1, 2, 3, 4, 5, 255, 254, 253])
        path = "/home/user/binary.bin"

        # Write binary file
        result = files_module.write_file_bytes(sandbox.sandbox_id, path, data)
        assert result["path"] == path

        # Read binary file back
        read_data = files_module.read_file_bytes(sandbox.sandbox_id, path)
        assert bytes(read_data) == data

    def test_read_binary_nonexistent(self, sandbox):
        """Test reading a non-existent binary file raises error."""
        with pytest.raises(FileNotFoundError):
            files_module.read_file_bytes(sandbox.sandbox_id, "/nonexistent.bin")


@pytest.mark.requires_images
class TestFileOperations:
    """Test various file operations."""

    def test_file_exists_true(self, sandbox):
        """Test checking if a file exists (true case)."""
        path = "/home/user/exists.txt"

        # Create file
        files_module.write_file(sandbox.sandbox_id, path, "content")

        # Check existence
        assert files_module.file_exists(sandbox.sandbox_id, path) is True

    def test_file_exists_false(self, sandbox):
        """Test checking if a file exists (false case)."""
        assert files_module.file_exists(sandbox.sandbox_id, "/nonexistent.txt") is False

    def test_get_file_info(self, sandbox):
        """Test getting file information."""
        path = "/home/user/info.txt"
        content = "test content"

        # Create file
        files_module.write_file(sandbox.sandbox_id, path, content)

        # Get info
        info = files_module.get_file_info(sandbox.sandbox_id, path)

        assert info["name"] == "info.txt"
        assert info["path"] == path
        assert info["type"] == "file"
        assert info["size"] >= len(content)
        assert "permissions" in info

    def test_get_directory_info(self, sandbox):
        """Test getting directory information."""
        path = "/home/user/testdir"

        # Create directory
        files_module.make_directory(sandbox.sandbox_id, path)

        # Get info
        info = files_module.get_file_info(sandbox.sandbox_id, path)

        assert info["name"] == "testdir"
        assert info["type"] == "dir"

    def test_remove_file(self, sandbox):
        """Test removing a file."""
        path = "/home/user/remove.txt"

        # Create file
        files_module.write_file(sandbox.sandbox_id, path, "content")

        # Remove it
        files_module.remove_file(sandbox.sandbox_id, path)

        # Verify it's gone
        assert files_module.file_exists(sandbox.sandbox_id, path) is False

    def test_remove_nonexistent_file(self, sandbox):
        """Test removing a non-existent file (should not raise error)."""
        # rm -rf doesn't fail on non-existent files
        files_module.remove_file(sandbox.sandbox_id, "/nonexistent.txt")


@pytest.mark.requires_images
class TestDirectoryOperations:
    """Test directory operations."""

    def test_make_directory(self, sandbox):
        """Test creating a directory."""
        path = "/home/user/newdir"

        result = files_module.make_directory(sandbox.sandbox_id, path)

        assert result is True
        assert files_module.file_exists(sandbox.sandbox_id, path) is True

    def test_make_directory_already_exists(self, sandbox):
        """Test creating a directory that already exists."""
        path = "/home/user/existingdir"

        # Create once
        files_module.make_directory(sandbox.sandbox_id, path)

        # Try to create again
        result = files_module.make_directory(sandbox.sandbox_id, path)

        assert result is False  # Already exists

    def test_make_nested_directory(self, sandbox):
        """Test creating nested directories."""
        path = "/home/user/level1/level2/level3"

        result = files_module.make_directory(sandbox.sandbox_id, path)

        assert result is True
        assert files_module.file_exists(sandbox.sandbox_id, path) is True

    def test_remove_directory(self, sandbox):
        """Test removing a directory."""
        path = "/home/user/removedir"

        # Create directory with a file
        files_module.make_directory(sandbox.sandbox_id, path)
        files_module.write_file(sandbox.sandbox_id, f"{path}/file.txt", "content")

        # Remove directory
        files_module.remove_file(sandbox.sandbox_id, path)

        # Verify it's gone
        assert files_module.file_exists(sandbox.sandbox_id, path) is False


@pytest.mark.requires_images
class TestRenameMove:
    """Test renaming and moving files."""

    def test_rename_file(self, sandbox):
        """Test renaming a file."""
        old_path = "/home/user/old.txt"
        new_path = "/home/user/new.txt"

        # Create file
        files_module.write_file(sandbox.sandbox_id, old_path, "content")

        # Rename
        result = files_module.rename_file(sandbox.sandbox_id, old_path, new_path)

        assert result["path"] == new_path
        assert files_module.file_exists(sandbox.sandbox_id, new_path) is True
        assert files_module.file_exists(sandbox.sandbox_id, old_path) is False

    def test_move_file_to_directory(self, sandbox):
        """Test moving a file to a different directory."""
        old_path = "/home/user/file.txt"
        new_dir = "/home/user/subdir"
        new_path = "/home/user/subdir/file.txt"

        # Create file and directory
        files_module.write_file(sandbox.sandbox_id, old_path, "content")
        files_module.make_directory(sandbox.sandbox_id, new_dir)

        # Move file
        files_module.rename_file(sandbox.sandbox_id, old_path, new_path)

        assert files_module.file_exists(sandbox.sandbox_id, new_path) is True
        assert files_module.file_exists(sandbox.sandbox_id, old_path) is False

    def test_rename_directory(self, sandbox):
        """Test renaming a directory."""
        old_path = "/home/user/olddir"
        new_path = "/home/user/newdir"

        # Create directory
        files_module.make_directory(sandbox.sandbox_id, old_path)

        # Rename
        files_module.rename_file(sandbox.sandbox_id, old_path, new_path)

        assert files_module.file_exists(sandbox.sandbox_id, new_path) is True
        assert files_module.file_exists(sandbox.sandbox_id, old_path) is False


@pytest.mark.requires_images
class TestUploadDownload:
    """Test file upload and download."""

    def test_upload_file(self, sandbox, temp_file):
        """Test uploading a file to sandbox."""
        remote_path = "/home/user/uploaded.txt"

        result = files_module.upload_file(
            sandbox.sandbox_id,
            str(temp_file),
            remote_path
        )

        assert result["path"] == remote_path
        assert result["size"] > 0

        # Verify file exists in sandbox
        assert files_module.file_exists(sandbox.sandbox_id, remote_path) is True

    def test_download_file(self, sandbox, tmp_path):
        """Test downloading a file from sandbox."""
        remote_path = "/home/user/download.txt"
        local_path = tmp_path / "downloaded.txt"
        content = "test download content"

        # Create file in sandbox
        files_module.write_file(sandbox.sandbox_id, remote_path, content)

        # Download
        result = files_module.download_file(
            sandbox.sandbox_id,
            remote_path,
            str(local_path)
        )

        assert result["path"] == str(local_path)
        assert result["size"] > 0

        # Verify file exists locally and has correct content
        assert local_path.exists()
        assert local_path.read_text() == content

    def test_upload_binary_file(self, sandbox, temp_binary_file):
        """Test uploading a binary file."""
        remote_path = "/home/user/binary.bin"

        result = files_module.upload_file(
            sandbox.sandbox_id,
            str(temp_binary_file),
            remote_path
        )

        assert result["path"] == remote_path

        # Download and verify
        downloaded_data = files_module.read_file_bytes(sandbox.sandbox_id, remote_path)
        original_data = temp_binary_file.read_bytes()

        assert bytes(downloaded_data) == original_data

    def test_upload_nonexistent_file(self, sandbox):
        """Test uploading a non-existent file raises error."""
        with pytest.raises(FileNotFoundError):
            files_module.upload_file(
                sandbox.sandbox_id,
                "/nonexistent/local/file.txt",
                "/home/user/remote.txt"
            )

    def test_download_nonexistent_file(self, sandbox, tmp_path):
        """Test downloading a non-existent file raises error."""
        with pytest.raises(FileNotFoundError):
            files_module.download_file(
                sandbox.sandbox_id,
                "/nonexistent/remote.txt",
                str(tmp_path / "local.txt")
            )


@pytest.mark.requires_images
class TestFileEdgeCases:
    """Test edge cases and error handling."""

    def test_write_file_with_unicode(self, sandbox):
        """Test writing a file with Unicode characters."""
        content = "Hello 世界 🌍 Ω α β"
        path = "/home/user/unicode.txt"

        files_module.write_file(sandbox.sandbox_id, path, content)

        read_content = files_module.read_file(sandbox.sandbox_id, path)
        assert read_content == content

    def test_write_file_with_newlines(self, sandbox):
        """Test writing a file with different newline styles."""
        content = "Line1\nLine2\r\nLine3\rLine4"
        path = "/home/user/newlines.txt"

        files_module.write_file(sandbox.sandbox_id, path, content)

        read_content = files_module.read_file(sandbox.sandbox_id, path)
        assert read_content == content

    def test_large_file_operations(self, sandbox):
        """Test operations with larger files."""
        # Create a ~1MB file
        content = "x" * (1024 * 1024)
        path = "/home/user/large.txt"

        files_module.write_file(sandbox.sandbox_id, path, content)

        read_content = files_module.read_file(sandbox.sandbox_id, path)
        assert len(read_content) == len(content)

    def test_file_with_spaces_in_name(self, sandbox):
        """Test file operations with spaces in filename."""
        path = "/home/user/file with spaces.txt"
        content = "test content"

        files_module.write_file(sandbox.sandbox_id, path, content)

        read_content = files_module.read_file(sandbox.sandbox_id, path)
        assert read_content == content

        assert files_module.file_exists(sandbox.sandbox_id, path) is True
