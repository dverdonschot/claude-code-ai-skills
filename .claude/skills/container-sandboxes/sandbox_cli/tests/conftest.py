"""
Pytest configuration and shared fixtures for docker-sandbox tests.
"""

import pytest
import docker
from pathlib import Path
import time


@pytest.fixture(scope="session")
def docker_client():
    """
    Provide a Docker client for tests.

    This fixture ensures Docker is running and accessible.
    """
    try:
        client = docker.from_env()
        client.ping()
        return client
    except Exception as e:
        pytest.skip(f"Docker is not running or accessible: {e}")


@pytest.fixture(scope="session")
def base_image(docker_client):
    """
    Ensure the base Docker image exists.

    If the image doesn't exist, skip tests that require it.
    """
    try:
        image = docker_client.images.get("docker-sandbox:base")
        return image
    except docker.errors.ImageNotFound:
        pytest.skip("docker-sandbox:base image not found. Run: cd docker && ./build-all.sh")


@pytest.fixture(scope="session")
def python_image(docker_client):
    """
    Ensure the Python Docker image exists.
    """
    try:
        image = docker_client.images.get("docker-sandbox:python")
        return image
    except docker.errors.ImageNotFound:
        pytest.skip("docker-sandbox:python image not found. Run: cd docker && ./build-all.sh")


@pytest.fixture
def sandbox(docker_client, base_image):
    """
    Create a test sandbox and clean it up after the test.

    Usage:
        def test_something(sandbox):
            # sandbox is a DockerSandbox instance
            result = sandbox.run_command("echo hello")
            assert result["exit_code"] == 0
    """
    from src.modules.sandbox import DockerSandbox

    # Create sandbox
    sbx = DockerSandbox.create(template="docker-sandbox:base")

    yield sbx

    # Cleanup
    try:
        sbx.container.stop(timeout=2)
        sbx.container.remove(force=True)
    except Exception:
        pass  # Already cleaned up


@pytest.fixture
def python_sandbox(docker_client, python_image):
    """
    Create a Python test sandbox and clean it up after the test.
    """
    from src.modules.sandbox import DockerSandbox

    # Create sandbox
    sbx = DockerSandbox.create(template="docker-sandbox:python")

    yield sbx

    # Cleanup
    try:
        sbx.container.stop(timeout=2)
        sbx.container.remove(force=True)
    except Exception:
        pass


@pytest.fixture
def temp_file(tmp_path):
    """
    Create a temporary file for testing file operations.

    Returns:
        Path: Path to the temporary file
    """
    test_file = tmp_path / "test_file.txt"
    test_file.write_text("test content")
    return test_file


@pytest.fixture
def temp_binary_file(tmp_path):
    """
    Create a temporary binary file for testing.

    Returns:
        Path: Path to the temporary binary file
    """
    test_file = tmp_path / "test_binary.bin"
    test_file.write_bytes(b"\x00\x01\x02\x03\x04\x05")
    return test_file


@pytest.fixture(autouse=True)
def cleanup_test_containers(docker_client):
    """
    Cleanup any leftover test containers after each test.

    This runs automatically after every test.
    """
    yield

    # Find and remove any test containers
    try:
        containers = docker_client.containers.list(
            all=True,
            filters={"label": "sandbox.type=docker-sandbox"}
        )
        for container in containers:
            # Only cleanup containers created in the last 5 minutes
            created_at = container.labels.get("sandbox.created_at", "0")
            if int(time.time()) - int(created_at) < 300:
                try:
                    container.stop(timeout=2)
                    container.remove(force=True)
                except Exception:
                    pass
    except Exception:
        pass


def pytest_configure(config):
    """
    Pytest configuration hook.
    """
    # Add custom markers
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "requires_images: marks tests that require Docker images built"
    )
