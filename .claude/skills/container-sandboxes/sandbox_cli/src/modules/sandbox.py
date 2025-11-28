"""
Sandbox lifecycle management using Docker/Podman containers.

Provides container-based sandbox creation, connection, and management
for safe, isolated code execution.
"""

import secrets
import time
from typing import Optional, Dict, List, Any
import docker
from docker.models.containers import Container
from docker.errors import NotFound, APIError
from .client import get_client


def resolve_sandbox_identifier(identifier: str) -> str:
    """
    Resolve a sandbox identifier (name or ID) to a container ID.

    Args:
        identifier: Container name or ID (short or full)

    Returns:
        Container ID

    Raises:
        NotFound: If container doesn't exist
    """
    client = get_client()
    try:
        # Try to get container by name or ID
        container = client.containers.get(identifier)
        return container.id[:12]  # Return short ID
    except NotFound:
        # If not found, try to find by name prefix
        containers = client.containers.list(all=True, filters={"name": identifier})
        if containers:
            return containers[0].id[:12]
        raise NotFound(f"Container not found: {identifier}")


class DockerSandbox:
    """
    Container-based sandbox for isolated code execution.

    Each sandbox is a Docker/Podman container with a unique ID and metadata.
    """

    def __init__(self, container: Container):
        """
        Initialize sandbox from existing Docker container.

        Args:
            container: Docker container object
        """
        self.container = container
        self.sandbox_id = container.id[:12]  # Use short container ID
        self.name = container.name  # Container name
        self._client = get_client()

    @classmethod
    def create(
        cls,
        template: Optional[str] = None,
        timeout: Optional[int] = None,
        envs: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, str]] = None,
        auto_pause: bool = False,
        ports: Optional[Dict[int, int]] = None,
        name: Optional[str] = None,
    ) -> "DockerSandbox":
        """
        Create a new sandbox (Docker container).

        Args:
            template: Docker image name (default: docker-sandbox:base)
            timeout: Auto-stop timeout in seconds (not implemented yet)
            envs: Environment variables
            metadata: Custom metadata stored as container labels
            auto_pause: Enable auto-pause (not implemented)
            ports: Port mappings {container_port: host_port}
            name: Custom container name (default: auto-generated)

        Returns:
            DockerSandbox instance

        Raises:
            docker.errors.ImageNotFound: If template image doesn't exist
            docker.errors.APIError: If Docker daemon is not running
        """
        client = get_client()

        # Default to base image
        image = template or "docker-sandbox:base"

        # Generate container name
        if name:
            # Use custom name, add csbx- prefix if not present
            container_name = name if name.startswith("csbx-") else f"csbx-{name}"
        else:
            # Generate unique container name
            random_suffix = secrets.token_hex(4)
            container_name = f"csbx-{random_suffix}"

        # Prepare labels for metadata
        labels = {
            "sandbox.created_at": str(int(time.time())),
            "sandbox.type": "docker-sandbox",
        }

        if timeout:
            labels["sandbox.timeout"] = str(timeout)

        if metadata:
            for key, value in metadata.items():
                labels[f"sandbox.metadata.{key}"] = str(value)

        # Prepare port bindings
        port_bindings = {}
        if ports:
            for container_port, host_port in ports.items():
                port_bindings[container_port] = host_port

        # Create and start container
        container = client.containers.run(
            image=image,
            name=container_name,
            detach=True,
            tty=True,
            stdin_open=True,
            environment=envs,
            labels=labels,
            remove=False,
            ports=port_bindings if port_bindings else None,
            command="sleep infinity",
        )

        return cls(container)

    @classmethod
    def connect(cls, sandbox_id: str, timeout: Optional[int] = None) -> "DockerSandbox":
        """
        Connect to an existing sandbox by ID.

        Args:
            sandbox_id: Container ID (short or full)
            timeout: Connection timeout (unused, for API compatibility)

        Returns:
            DockerSandbox instance

        Raises:
            docker.errors.NotFound: If container doesn't exist
        """
        client = get_client()
        container = client.containers.get(sandbox_id)
        return cls(container)

    @classmethod
    def kill(cls, sandbox_id: str) -> bool:
        """
        Kill and remove a sandbox.

        Args:
            sandbox_id: Container ID to kill

        Returns:
            True if killed, False if not found
        """
        try:
            client = get_client()
            container = client.containers.get(sandbox_id)
            container.stop(timeout=5)
            container.remove()
            return True
        except NotFound:
            return False

    @classmethod
    def list(cls, limit: int = 20) -> List["DockerSandbox"]:
        """
        List all running sandboxes.

        Args:
            limit: Maximum number of sandboxes to return

        Returns:
            List of DockerSandbox instances
        """
        client = get_client()

        # Filter containers with sandbox label
        containers = client.containers.list(
            filters={"label": "sandbox.type=docker-sandbox"},
            limit=limit,
        )

        return [cls(container) for container in containers]

    @classmethod
    def get_info(cls, sandbox_id: str) -> Dict[str, Any]:
        """
        Get sandbox information.

        Args:
            sandbox_id: Container ID

        Returns:
            Dictionary with sandbox info
        """
        client = get_client()
        container = client.containers.get(sandbox_id)

        labels = container.labels

        # Extract metadata from labels
        metadata = {}
        for key, value in labels.items():
            if key.startswith("sandbox.metadata."):
                metadata_key = key.replace("sandbox.metadata.", "")
                metadata[metadata_key] = value

        return {
            "sandbox_id": container.id[:12],
            "name": container.name,
            "template_id": container.image.tags[0] if container.image.tags else "unknown",
            "started_at": labels.get("sandbox.created_at", "unknown"),
            "metadata": metadata,
            "status": container.status,
        }

    @classmethod
    def beta_pause(cls, sandbox_id: str) -> None:
        """
        Pause a sandbox (beta feature).

        Args:
            sandbox_id: Container ID to pause
        """
        client = get_client()
        container = client.containers.get(sandbox_id)
        container.pause()

    @classmethod
    def beta_resume(cls, sandbox_id: str) -> None:
        """
        Resume a paused sandbox (beta feature).

        Args:
            sandbox_id: Container ID to resume
        """
        client = get_client()
        container = client.containers.get(sandbox_id)
        container.unpause()

    def is_running(self) -> bool:
        """
        Check if sandbox is running.

        Returns:
            True if running, False otherwise
        """
        self.container.reload()
        return self.container.status == "running"

    def get_host(self, port: int) -> str:
        """
        Get the public hostname for an exposed port.

        For Docker, this returns localhost:mapped_port.

        Args:
            port: Container port number

        Returns:
            URL in format http://localhost:mapped_port
        """
        self.container.reload()

        # Get port mappings
        port_mappings = self.container.ports

        # Find the mapped host port
        port_key = f"{port}/tcp"
        if port_key in port_mappings and port_mappings[port_key]:
            host_port = port_mappings[port_key][0]["HostPort"]
            return f"http://localhost:{host_port}"

        # If no mapping found, return the container port
        # (assuming direct access or same port mapping)
        return f"http://localhost:{port}"

    def stop(self, timeout: int = 10) -> None:
        """
        Stop the sandbox container.

        Args:
            timeout: Seconds to wait before killing
        """
        self.container.stop(timeout=timeout)

    def remove(self) -> None:
        """Remove the sandbox container."""
        self.container.remove(force=True)


# Helper functions for functional API

def create_sandbox(
    template: Optional[str] = None,
    timeout: Optional[int] = None,
    envs: Optional[Dict[str, str]] = None,
    metadata: Optional[Dict[str, str]] = None,
    auto_pause: bool = False,
    ports: Optional[Dict[int, int]] = None,
    name: Optional[str] = None,
) -> DockerSandbox:
    """
    Create a new sandbox.

    See DockerSandbox.create() for details.
    """
    return DockerSandbox.create(
        template=template,
        timeout=timeout,
        envs=envs,
        metadata=metadata,
        auto_pause=auto_pause,
        ports=ports,
        name=name,
    )


def get_sandbox(sandbox_id: str, timeout: Optional[int] = None) -> DockerSandbox:
    """
    Connect to an existing sandbox.

    See DockerSandbox.connect() for details.
    """
    return DockerSandbox.connect(sandbox_id, timeout=timeout)


def kill_sandbox(sandbox_id: str) -> bool:
    """
    Kill a sandbox.

    See DockerSandbox.kill() for details.
    """
    return DockerSandbox.kill(sandbox_id)


def list_sandboxes(limit: int = 20) -> List[Dict[str, Any]]:
    """
    List all running sandboxes.

    Args:
        limit: Maximum number to return

    Returns:
        List of sandbox info dictionaries
    """
    sandboxes = DockerSandbox.list(limit=limit)
    return [DockerSandbox.get_info(sbx.sandbox_id) for sbx in sandboxes]


def get_sandbox_info(sandbox_id: str) -> Dict[str, Any]:
    """
    Get sandbox information.

    See DockerSandbox.get_info() for details.
    """
    return DockerSandbox.get_info(sandbox_id)


def is_sandbox_running(sandbox_id: str) -> bool:
    """
    Check if a sandbox is running.

    Args:
        sandbox_id: Container ID

    Returns:
        True if running, False otherwise
    """
    try:
        sbx = get_sandbox(sandbox_id)
        return sbx.is_running()
    except NotFound:
        return False


def pause_sandbox(sandbox_id: str) -> None:
    """
    Pause a sandbox (beta).

    See DockerSandbox.beta_pause() for details.
    """
    DockerSandbox.beta_pause(sandbox_id)


def resume_sandbox(sandbox_id: str) -> None:
    """
    Resume a paused sandbox (beta).

    See DockerSandbox.beta_resume() for details.
    """
    DockerSandbox.beta_resume(sandbox_id)


def get_host(sandbox_id: str, port: int) -> str:
    """
    Get the public URL for an exposed port.

    Args:
        sandbox_id: Container ID
        port: Port number

    Returns:
        URL string
    """
    sbx = get_sandbox(sandbox_id)
    return sbx.get_host(port)
