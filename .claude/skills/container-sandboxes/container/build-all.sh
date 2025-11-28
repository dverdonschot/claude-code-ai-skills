#!/bin/bash
# Build all container sandbox images in correct order
# Supports both Docker and Podman

set -e

# Detect container runtime
RUNTIME="${CONTAINER_RUNTIME:-auto}"

detect_runtime() {
    if [ "$RUNTIME" = "auto" ]; then
        if command -v podman &> /dev/null; then
            echo "podman"
        elif command -v docker &> /dev/null; then
            echo "docker"
        else
            echo "ERROR: Neither Docker nor Podman found. Please install one of them." >&2
            exit 1
        fi
    else
        echo "$RUNTIME"
    fi
}

RUNTIME=$(detect_runtime)

echo "========================================="
echo "Building Container Sandbox Images"
echo "Using runtime: $RUNTIME"
echo "========================================="

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Build base image first
echo -e "\n[1/4] Building base image..."
$RUNTIME build -t container-sandbox:base ./base/

# Build Python image
echo -e "\n[2/4] Building Python image (with uv)..."
$RUNTIME build -t container-sandbox:python ./python/

# Build Node image
echo -e "\n[3/4] Building Node.js image..."
$RUNTIME build -t container-sandbox:node ./node/

# Build full-stack image
echo -e "\n[4/4] Building full-stack image (Python + Node + uv)..."
$RUNTIME build -t container-sandbox:full-stack ./full-stack/

echo -e "\n========================================="
echo "All images built successfully!"
echo "========================================="

# List images
echo -e "\nBuilt images:"
$RUNTIME images | grep container-sandbox

echo -e "\nUsage:"
echo "  $RUNTIME run -it --rm container-sandbox:base bash"
echo "  $RUNTIME run -it --rm container-sandbox:python python"
echo "  $RUNTIME run -it --rm container-sandbox:node node"
echo "  $RUNTIME run -it --rm container-sandbox:full-stack bash"
echo -e "\nTo use a specific runtime, set CONTAINER_RUNTIME:"
echo "  CONTAINER_RUNTIME=docker ./build-all.sh"
echo "  CONTAINER_RUNTIME=podman ./build-all.sh"
