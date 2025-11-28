"""
Docker/Podman client management.
"""

import os
import shutil
import docker
from .. import config

def get_podman_socket() -> str:
    """Find the Podman socket path."""
    # Check if user provided a path
    if config.PODMAN_SOCKET_PATH:
        return config.PODMAN_SOCKET_PATH

    # Check XDG_RUNTIME_DIR
    xdg_runtime = os.environ.get("XDG_RUNTIME_DIR")
    if xdg_runtime:
        socket_path = os.path.join(xdg_runtime, "podman", "podman.sock")
        if os.path.exists(socket_path):
            return f"unix://{socket_path}"

    # Check user run directory
    uid = os.getuid()
    user_socket = f"/run/user/{uid}/podman/podman.sock"
    if os.path.exists(user_socket):
        return f"unix://{user_socket}"

    # Check system directory
    system_socket = "/run/podman/podman.sock"
    if os.path.exists(system_socket):
        return f"unix://{system_socket}"

    # Fallback to user socket path even if not found (let docker-py raise error)
    return f"unix:///run/user/{uid}/podman/podman.sock"

def detect_runtime() -> str:
    """
    Auto-detect which container runtime is available.
    Checks for Podman first, then Docker.

    Returns:
        "podman" or "docker"

    Raises:
        RuntimeError if neither is available
    """
    if shutil.which("podman"):
        return "podman"
    elif shutil.which("docker"):
        return "docker"
    else:
        raise RuntimeError(
            "No container runtime found. Please install Docker or Podman."
        )

def get_client() -> docker.DockerClient:
    """
    Get a container client instance.

    Supports both Docker and Podman runtimes based on configuration.
    If CONTAINER_RUNTIME is "auto", detects available runtime.

    Returns:
        docker.DockerClient instance connected to the appropriate runtime

    Raises:
        RuntimeError if no runtime is available
    """
    runtime = config.CONTAINER_RUNTIME

    # Auto-detect if needed
    if runtime == "auto":
        runtime = detect_runtime()

    # Connect to the appropriate runtime
    if runtime == "podman":
        base_url = get_podman_socket()
        return docker.DockerClient(base_url=base_url)
    elif runtime == "docker":
        return docker.from_env()
    else:
        raise ValueError(
            f"Invalid CONTAINER_RUNTIME: {runtime}. Use 'auto', 'docker', or 'podman'."
        )
