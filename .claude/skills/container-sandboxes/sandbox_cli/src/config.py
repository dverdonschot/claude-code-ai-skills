"""
Global configuration for the CLI.
"""

import os

# Container runtime configuration
# AUTO will detect podman first, then docker
# Set CONTAINER_RUNTIME environment variable to override
CONTAINER_RUNTIME = os.getenv("CONTAINER_RUNTIME", "auto")  # auto, docker, or podman

# Legacy compatibility
USE_PODMAN = CONTAINER_RUNTIME == "podman"
PODMAN_SOCKET_PATH = os.getenv("PODMAN_SOCKET_PATH", None)
