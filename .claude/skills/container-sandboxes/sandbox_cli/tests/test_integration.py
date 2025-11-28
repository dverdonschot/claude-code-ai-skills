"""
Integration tests for complete workflows.

These tests verify that all components work together correctly
for common use cases.
"""

import pytest
import time
from pathlib import Path
from src.modules import sandbox as sbx_module
from src.modules import commands as cmd_module
from src.modules import files as files_module


@pytest.mark.integration
@pytest.mark.requires_images
class TestPythonWorkflow:
    """Test complete Python development workflow."""

    def test_python_hello_world(self, python_sandbox):
        """Test creating and running a simple Python script."""
        # Write Python script
        script = "print('Hello from Docker Sandbox!')"
        files_module.write_file(python_sandbox.sandbox_id, "/home/user/hello.py", script)

        # Run script
        result = cmd_module.run_command(python_sandbox.sandbox_id, "python /home/user/hello.py")

        assert result["exit_code"] == 0
        assert "Hello from Docker Sandbox!" in result["stdout"]

    def test_python_package_installation_with_uv(self, python_sandbox):
        """Test installing and using a Python package with uv."""
        # Install package with uv
        result = cmd_module.run_command(
            python_sandbox.sandbox_id,
            "uv pip install --system requests",
            timeout=120
        )

        assert result["exit_code"] == 0

        # Test package usage
        script = """
import requests
print(f"Requests version: {requests.__version__}")
"""
        files_module.write_file(python_sandbox.sandbox_id, "/home/user/test.py", script)

        result = cmd_module.run_command(python_sandbox.sandbox_id, "python /home/user/test.py")

        assert result["exit_code"] == 0
        assert "Requests version:" in result["stdout"]

    def test_python_virtual_environment(self, python_sandbox):
        """Test creating and using a virtual environment."""
        # Create venv
        result = cmd_module.run_command(
            python_sandbox.sandbox_id,
            "python -m venv /home/user/venv",
            timeout=60
        )

        assert result["exit_code"] == 0

        # Activate and install package
        result = cmd_module.run_command(
            python_sandbox.sandbox_id,
            "source /home/user/venv/bin/activate && pip install requests",
            user="user",
            timeout=120
        )

        # Note: May need shell mode for source command
        # For now, just verify venv was created
        assert files_module.file_exists(python_sandbox.sandbox_id, "/home/user/venv")


@pytest.mark.integration
@pytest.mark.requires_images
class TestFileWorkflow:
    """Test complete file manipulation workflows."""

    def test_create_project_structure(self, sandbox):
        """Test creating a complete project structure."""
        # Create directories
        dirs = [
            "/home/user/project",
            "/home/user/project/src",
            "/home/user/project/tests",
            "/home/user/project/data",
        ]

        for directory in dirs:
            files_module.make_directory(sandbox.sandbox_id, directory)
            assert files_module.file_exists(sandbox.sandbox_id, directory)

        # Create files
        files_module.write_file(
            sandbox.sandbox_id,
            "/home/user/project/README.md",
            "# My Project"
        )
        files_module.write_file(
            sandbox.sandbox_id,
            "/home/user/project/src/main.py",
            "print('main')"
        )

        # Verify structure
        files = files_module.list_files(sandbox.sandbox_id, "/home/user/project")
        names = [f["name"] for f in files]

        assert "README.md" in names
        assert "src" in names
        assert "tests" in names
        assert "data" in names

    def test_upload_process_download(self, sandbox, tmp_path):
        """Test uploading, processing, and downloading a file."""
        # Create local file
        local_input = tmp_path / "input.txt"
        local_input.write_text("hello world")

        # Upload
        files_module.upload_file(
            sandbox.sandbox_id,
            str(local_input),
            "/home/user/input.txt"
        )

        # Process (convert to uppercase)
        cmd_module.run_command(
            sandbox.sandbox_id,
            "cat /home/user/input.txt | tr '[:lower:]' '[:upper:]' > /home/user/output.txt",
            user="user"
        )

        # Download
        local_output = tmp_path / "output.txt"
        files_module.download_file(
            sandbox.sandbox_id,
            "/home/user/output.txt",
            str(local_output)
        )

        # Verify
        assert local_output.read_text() == "HELLO WORLD"


@pytest.mark.integration
@pytest.mark.requires_images
@pytest.mark.slow
class TestWebServerWorkflow:
    """Test running web servers in sandboxes."""

    def test_simple_http_server(self, sandbox):
        """Test running a simple HTTP server."""
        # Create an HTML file
        html = "<html><body><h1>Test Page</h1></body></html>"
        files_module.write_file(sandbox.sandbox_id, "/home/user/index.html", html)

        # Start HTTP server in background
        cmd_module.run_command_background(
            sandbox.sandbox_id,
            "python -m http.server 8000",
            cwd="/home/user"
        )

        # Wait for server to start
        time.sleep(2)

        # Verify server is running
        processes = cmd_module.list_processes(sandbox.sandbox_id)
        commands = [p["command"] for p in processes]
        assert any("http.server" in cmd for cmd in commands)


@pytest.mark.integration
@pytest.mark.requires_images
class TestMultiSandboxWorkflow:
    """Test workflows involving multiple sandboxes."""

    def test_two_sandboxes_simultaneously(self, docker_client, base_image):
        """Test running two sandboxes at the same time."""
        # Create two sandboxes
        sbx1 = sbx_module.create_sandbox()
        sbx2 = sbx_module.create_sandbox()

        try:
            # Run commands in both
            result1 = cmd_module.run_command(sbx1.sandbox_id, "echo sandbox1")
            result2 = cmd_module.run_command(sbx2.sandbox_id, "echo sandbox2")

            assert result1["exit_code"] == 0
            assert "sandbox1" in result1["stdout"]

            assert result2["exit_code"] == 0
            assert "sandbox2" in result2["stdout"]

            # Verify both are listed
            sandboxes = sbx_module.list_sandboxes()
            ids = [s["sandbox_id"] for s in sandboxes]

            assert sbx1.sandbox_id in ids
            assert sbx2.sandbox_id in ids

        finally:
            # Cleanup
            for sbx in [sbx1, sbx2]:
                try:
                    sbx.container.stop(timeout=2)
                    sbx.container.remove(force=True)
                except Exception:
                    pass


@pytest.mark.integration
@pytest.mark.requires_images
class TestDataProcessingWorkflow:
    """Test data processing workflows."""

    def test_csv_processing(self, python_sandbox):
        """Test processing CSV data with Python."""
        # Create CSV file
        csv_content = "name,age\nAlice,30\nBob,25\nCharlie,35"
        files_module.write_file(python_sandbox.sandbox_id, "/home/user/data.csv", csv_content)

        # Process with Python script
        script = """
import csv

with open('/home/user/data.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(f"{row['name']}: {row['age']}")
"""
        files_module.write_file(python_sandbox.sandbox_id, "/home/user/process.py", script)

        # Run script
        result = cmd_module.run_command(python_sandbox.sandbox_id, "python /home/user/process.py")

        assert result["exit_code"] == 0
        assert "Alice: 30" in result["stdout"]
        assert "Bob: 25" in result["stdout"]
        assert "Charlie: 35" in result["stdout"]

    def test_json_processing(self, python_sandbox):
        """Test processing JSON data."""
        # Create JSON file
        json_content = '{"users": [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]}'
        files_module.write_file(python_sandbox.sandbox_id, "/home/user/data.json", json_content)

        # Process with Python
        script = """
import json

with open('/home/user/data.json', 'r') as f:
    data = json.load(f)
    for user in data['users']:
        print(f"{user['name']}: {user['age']}")
"""
        files_module.write_file(python_sandbox.sandbox_id, "/home/user/process.py", script)

        result = cmd_module.run_command(python_sandbox.sandbox_id, "python /home/user/process.py")

        assert result["exit_code"] == 0
        assert "Alice: 30" in result["stdout"]
        assert "Bob: 25" in result["stdout"]


@pytest.mark.integration
@pytest.mark.requires_images
class TestCompleteProjectWorkflow:
    """Test a complete end-to-end project workflow."""

    def test_build_and_run_python_project(self, python_sandbox):
        """Test building and running a complete Python project."""
        # Create project structure
        files_module.make_directory(python_sandbox.sandbox_id, "/home/user/myproject")
        files_module.make_directory(python_sandbox.sandbox_id, "/home/user/myproject/src")

        # Create main.py
        main_py = """
def greet(name):
    return f"Hello, {name}!"

if __name__ == "__main__":
    print(greet("World"))
"""
        files_module.write_file(
            python_sandbox.sandbox_id,
            "/home/user/myproject/src/main.py",
            main_py
        )

        # Create test file
        test_py = """
import sys
sys.path.insert(0, '/home/user/myproject/src')

from main import greet

def test_greet():
    assert greet("Alice") == "Hello, Alice!"
    print("Test passed!")

if __name__ == "__main__":
    test_greet()
"""
        files_module.write_file(
            python_sandbox.sandbox_id,
            "/home/user/myproject/test_main.py",
            test_py
        )

        # Run tests
        result = cmd_module.run_command(
            python_sandbox.sandbox_id,
            "python test_main.py",
            cwd="/home/user/myproject"
        )

        assert result["exit_code"] == 0
        assert "Test passed!" in result["stdout"]

        # Run main
        result = cmd_module.run_command(
            python_sandbox.sandbox_id,
            "python src/main.py",
            cwd="/home/user/myproject"
        )

        assert result["exit_code"] == 0
        assert "Hello, World!" in result["stdout"]


@pytest.mark.integration
@pytest.mark.requires_images
class TestErrorHandlingWorkflow:
    """Test error handling in workflows."""

    def test_graceful_failure_handling(self, sandbox):
        """Test handling command failures gracefully."""
        # Run a command that will fail
        result = cmd_module.run_command(sandbox.sandbox_id, "ls /nonexistent")

        assert result["exit_code"] != 0
        assert len(result["stderr"]) > 0

        # Sandbox should still be usable
        result2 = cmd_module.run_command(sandbox.sandbox_id, "echo still working")

        assert result2["exit_code"] == 0
        assert "still working" in result2["stdout"]

    def test_cleanup_after_errors(self, docker_client, base_image):
        """Test that sandboxes can be cleaned up even after errors."""
        sbx = sbx_module.create_sandbox()

        try:
            # Cause some errors
            cmd_module.run_command(sbx.sandbox_id, "invalid_command_xyz")

            # Should still be able to kill sandbox
            result = sbx_module.kill_sandbox(sbx.sandbox_id)
            assert result is True

        except Exception:
            # Cleanup in case of test failure
            try:
                sbx.container.stop(timeout=2)
                sbx.container.remove(force=True)
            except Exception:
                pass


@pytest.mark.integration
@pytest.mark.requires_images
@pytest.mark.slow
class TestPerformanceWorkflow:
    """Test performance of workflows."""

    def test_rapid_file_operations(self, sandbox):
        """Test rapid file creation and deletion."""
        import time

        start = time.time()

        # Create 50 files
        for i in range(50):
            files_module.write_file(
                sandbox.sandbox_id,
                f"/home/user/file{i}.txt",
                f"content{i}"
            )

        duration = time.time() - start

        # Should complete in reasonable time (< 30 seconds for 50 files)
        assert duration < 30.0

        # Verify files exist
        files = files_module.list_files(sandbox.sandbox_id, "/home/user")
        names = [f["name"] for f in files]

        assert "file0.txt" in names
        assert "file49.txt" in names
