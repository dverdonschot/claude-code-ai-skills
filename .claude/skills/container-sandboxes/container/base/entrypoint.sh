#!/bin/bash
# Base container entrypoint script

set -e

# Print startup message
echo "Docker Sandbox Container - Base Image"
echo "Working directory: $(pwd)"
echo "User: $(whoami)"
echo "----------------------------------------"

# Execute the command passed to the container
exec "$@"
