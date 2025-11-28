"""
Unit tests for sandbox lifecycle management (sandbox.py).
"""

import pytest
import docker
from src.modules import sandbox as sbx_module


@pytest.mark.requires_images
class TestDockerSandboxCreate:
    """Test sandbox creation functionality."""

    def test_create_basic_sandbox(self, docker_client, base_image):
        """Test creating a basic sandbox with default settings."""
        sbx = sbx_module.create_sandbox()

        try:
            assert sbx.sandbox_id is not None
            assert len(sbx.sandbox_id) == 12  # Short container ID
            assert sbx.is_running()
        finally:
            sbx.container.stop(timeout=2)
            sbx.container.remove(force=True)

    def test_create_sandbox_with_template(self, docker_client, python_image):
        """Test creating a sandbox with a specific template."""
        sbx = sbx_module.create_sandbox(template="docker-sandbox:python")

        try:
            assert sbx.sandbox_id is not None
            assert sbx.is_running()

            # Verify Python is available
            result = docker_client.containers.get(sbx.sandbox_id).exec_run("python --version")
            assert result.exit_code == 0
            assert b"Python 3.12" in result.output
        finally:
            sbx.container.stop(timeout=2)
            sbx.container.remove(force=True)

    def test_create_sandbox_with_envs(self, docker_client, base_image):
        """Test creating a sandbox with environment variables."""
        envs = {"TEST_VAR": "test_value", "ANOTHER_VAR": "another_value"}
        sbx = sbx_module.create_sandbox(envs=envs)

        try:
            # Verify environment variables are set
            result = docker_client.containers.get(sbx.sandbox_id).exec_run("env")
            output = result.output.decode()

            assert "TEST_VAR=test_value" in output
            assert "ANOTHER_VAR=another_value" in output
        finally:
            sbx.container.stop(timeout=2)
            sbx.container.remove(force=True)

    def test_create_sandbox_with_metadata(self, docker_client, base_image):
        """Test creating a sandbox with metadata."""
        metadata = {"name": "test-sandbox", "purpose": "testing"}
        sbx = sbx_module.create_sandbox(metadata=metadata)

        try:
            # Verify metadata is stored in labels
            container = docker_client.containers.get(sbx.sandbox_id)
            labels = container.labels

            assert "sandbox.metadata.name" in labels
            assert labels["sandbox.metadata.name"] == "test-sandbox"
            assert "sandbox.metadata.purpose" in labels
            assert labels["sandbox.metadata.purpose"] == "testing"
        finally:
            sbx.container.stop(timeout=2)
            sbx.container.remove(force=True)

    def test_create_sandbox_with_ports(self, docker_client, base_image):
        """Test creating a sandbox with port mappings."""
        ports = {5173: 5173, 8000: 8000}
        sbx = sbx_module.create_sandbox(ports=ports)

        try:
            # Verify ports are mapped
            container = docker_client.containers.get(sbx.sandbox_id)
            container.reload()
            port_bindings = container.ports

            assert "5173/tcp" in port_bindings
            assert "8000/tcp" in port_bindings
        finally:
            sbx.container.stop(timeout=2)
            sbx.container.remove(force=True)


@pytest.mark.requires_images
class TestDockerSandboxConnect:
    """Test connecting to existing sandboxes."""

    def test_connect_to_existing_sandbox(self, sandbox):
        """Test connecting to an existing sandbox by ID."""
        # Connect using the sandbox ID
        connected_sbx = sbx_module.get_sandbox(sandbox.sandbox_id)

        assert connected_sbx.sandbox_id == sandbox.sandbox_id
        assert connected_sbx.is_running()

    def test_connect_to_nonexistent_sandbox(self, docker_client):
        """Test connecting to a non-existent sandbox raises error."""
        with pytest.raises(docker.errors.NotFound):
            sbx_module.get_sandbox("nonexistent_id")


@pytest.mark.requires_images
class TestDockerSandboxKill:
    """Test killing sandboxes."""

    def test_kill_existing_sandbox(self, docker_client, base_image):
        """Test killing an existing sandbox."""
        # Create a sandbox
        sbx = sbx_module.create_sandbox()
        sandbox_id = sbx.sandbox_id

        # Kill it
        result = sbx_module.kill_sandbox(sandbox_id)
        assert result is True

        # Verify it's gone
        with pytest.raises(docker.errors.NotFound):
            docker_client.containers.get(sandbox_id)

    def test_kill_nonexistent_sandbox(self):
        """Test killing a non-existent sandbox returns False."""
        result = sbx_module.kill_sandbox("nonexistent_id")
        assert result is False


@pytest.mark.requires_images
class TestDockerSandboxList:
    """Test listing sandboxes."""

    def test_list_sandboxes_empty(self, docker_client):
        """Test listing sandboxes when none exist."""
        # Clean up any existing test sandboxes first
        containers = docker_client.containers.list(
            filters={"label": "sandbox.type=docker-sandbox"}
        )
        for container in containers:
            try:
                container.stop(timeout=2)
                container.remove(force=True)
            except Exception:
                pass

        sandboxes = sbx_module.list_sandboxes()
        assert isinstance(sandboxes, list)
        assert len(sandboxes) == 0

    def test_list_sandboxes_with_containers(self, sandbox):
        """Test listing sandboxes when some exist."""
        sandboxes = sbx_module.list_sandboxes()

        assert isinstance(sandboxes, list)
        assert len(sandboxes) >= 1

        # Verify our sandbox is in the list
        sandbox_ids = [s["sandbox_id"] for s in sandboxes]
        assert sandbox.sandbox_id in sandbox_ids


@pytest.mark.requires_images
class TestDockerSandboxInfo:
    """Test getting sandbox information."""

    def test_get_sandbox_info(self, sandbox):
        """Test getting information about a sandbox."""
        info = sbx_module.get_sandbox_info(sandbox.sandbox_id)

        assert isinstance(info, dict)
        assert info["sandbox_id"] == sandbox.sandbox_id
        assert "template_id" in info
        assert "started_at" in info
        assert "metadata" in info
        assert "status" in info

    def test_get_sandbox_info_with_metadata(self, docker_client, base_image):
        """Test getting info for sandbox with metadata."""
        metadata = {"name": "test", "version": "1.0"}
        sbx = sbx_module.create_sandbox(metadata=metadata)

        try:
            info = sbx_module.get_sandbox_info(sbx.sandbox_id)

            assert info["metadata"]["name"] == "test"
            assert info["metadata"]["version"] == "1.0"
        finally:
            sbx.container.stop(timeout=2)
            sbx.container.remove(force=True)


@pytest.mark.requires_images
class TestDockerSandboxStatus:
    """Test checking sandbox status."""

    def test_is_running_true(self, sandbox):
        """Test checking if a running sandbox is running."""
        assert sandbox.is_running() is True
        assert sbx_module.is_sandbox_running(sandbox.sandbox_id) is True

    def test_is_running_stopped(self, docker_client, base_image):
        """Test checking if a stopped sandbox is not running."""
        sbx = sbx_module.create_sandbox()
        sandbox_id = sbx.sandbox_id

        # Stop the sandbox
        sbx.container.stop(timeout=2)

        try:
            assert sbx.is_running() is False
        finally:
            sbx.container.remove(force=True)

    def test_is_running_nonexistent(self):
        """Test checking if a non-existent sandbox is not running."""
        assert sbx_module.is_sandbox_running("nonexistent_id") is False


@pytest.mark.requires_images
class TestDockerSandboxPauseResume:
    """Test pausing and resuming sandboxes."""

    def test_pause_and_resume_sandbox(self, sandbox):
        """Test pausing and resuming a sandbox."""
        # Pause
        sbx_module.pause_sandbox(sandbox.sandbox_id)

        # Check status
        sandbox.container.reload()
        assert sandbox.container.status == "paused"

        # Resume
        sbx_module.resume_sandbox(sandbox.sandbox_id)

        # Check status
        sandbox.container.reload()
        assert sandbox.container.status == "running"


@pytest.mark.requires_images
class TestDockerSandboxGetHost:
    """Test getting public URLs for sandboxes."""

    def test_get_host_with_port_mapping(self, docker_client, base_image):
        """Test getting host URL for a mapped port."""
        ports = {5173: 5173}
        sbx = sbx_module.create_sandbox(ports=ports)

        try:
            url = sbx_module.get_host(sbx.sandbox_id, 5173)

            assert url.startswith("http://localhost:")
            assert "5173" in url
        finally:
            sbx.container.stop(timeout=2)
            sbx.container.remove(force=True)

    def test_get_host_without_port_mapping(self, sandbox):
        """Test getting host URL for a non-mapped port."""
        # Should still return a URL (assumes direct access)
        url = sbx_module.get_host(sandbox.sandbox_id, 8080)

        assert url.startswith("http://localhost:")


@pytest.mark.requires_images
class TestDockerSandboxMethods:
    """Test instance methods of DockerSandbox class."""

    def test_sandbox_stop(self, docker_client, base_image):
        """Test stopping a sandbox."""
        sbx = sbx_module.create_sandbox()

        try:
            sbx.stop()

            # Verify it's stopped
            sbx.container.reload()
            assert sbx.container.status in ["exited", "stopped"]
        finally:
            sbx.container.remove(force=True)

    def test_sandbox_remove(self, docker_client, base_image):
        """Test removing a sandbox."""
        sbx = sbx_module.create_sandbox()
        sandbox_id = sbx.sandbox_id

        sbx.stop()
        sbx.remove()

        # Verify it's gone
        with pytest.raises(docker.errors.NotFound):
            docker_client.containers.get(sandbox_id)
