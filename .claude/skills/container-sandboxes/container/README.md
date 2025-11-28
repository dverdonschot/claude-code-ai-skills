# Container Sandbox Images

This directory contains container image definitions for various sandbox environments.
Supports both **Docker** and **Podman** as container runtimes.

## Available Images

### 1. Base Image (`base/`)
**Tag:** `container-sandbox:base`

Minimal Ubuntu 22.04 environment with essential utilities.

**Includes:**
- Core utilities (curl, wget, git, vim, nano)
- Build tools (build-essential)
- Network tools (net-tools, iputils-ping)
- Process management (procps)
- Non-root user: `user` (UID 1000)

**Build:**
```bash
# Docker
docker build -t container-sandbox:base ./base/

# Podman
podman build -t container-sandbox:base ./base/
```

### 2. Python Image (`python/`)
**Tag:** `container-sandbox:python`

Python development environment extending the base image.

**Includes:**
- Python 3.12 (from deadsnakes PPA)
- **uv** - Astral's fast Python package installer and project manager
- pip package manager
- Common packages: flask, fastapi, numpy, pandas, pytest
- Data science tools: matplotlib, seaborn

**Build:**
```bash
# Requires base image built first
# Docker
docker build -t container-sandbox:python ./python/

# Podman
podman build -t container-sandbox:python ./python/
```

### 3. Node.js Image (`node/`)
**Tag:** `container-sandbox:node`

Node.js development environment extending the base image.

**Includes:**
- Node.js 22 LTS
- npm, yarn, pnpm
- TypeScript, Vite, ESLint, Prettier
- Common dev tools

**Build:**
```bash
# Requires base image built first
# Docker
docker build -t container-sandbox:node ./node/

# Podman
podman build -t container-sandbox:node ./node/
```

### 4. Full-Stack Image (`full-stack/`)
**Tag:** `container-sandbox:full-stack`

Combined Python + Node.js environment for full-stack development.

**Includes:**
- Everything from Python image (including **uv**)
- Everything from Node image
- Database clients: sqlite3, postgresql-client, redis-tools

**Build:**
```bash
# Requires base image built first
# Docker
docker build -t container-sandbox:full-stack ./full-stack/

# Podman
podman build -t container-sandbox:full-stack ./full-stack/
```

## Build All Images

The build script automatically detects your container runtime (Docker or Podman):

```bash
./build-all.sh
```

Or specify a runtime explicitly:

```bash
# Use Docker
CONTAINER_RUNTIME=docker ./build-all.sh

# Use Podman
CONTAINER_RUNTIME=podman ./build-all.sh
```

Manual build (Docker):
```bash
docker build -t container-sandbox:base ./base/
docker build -t container-sandbox:python ./python/
docker build -t container-sandbox:node ./node/
docker build -t container-sandbox:full-stack ./full-stack/
```

Manual build (Podman):
```bash
podman build -t container-sandbox:base ./base/
podman build -t container-sandbox:python ./python/
podman build -t container-sandbox:node ./node/
podman build -t container-sandbox:full-stack ./full-stack/
```

## Usage

### Run a container

With Docker:
```bash
# Base
docker run -it --rm container-sandbox:base bash

# Python (with uv available)
docker run -it --rm container-sandbox:python python
docker run -it --rm container-sandbox:python uv --version

# Node
docker run -it --rm container-sandbox:node node

# Full-stack
docker run -it --rm container-sandbox:full-stack bash
```

With Podman:
```bash
# Base
podman run -it --rm container-sandbox:base bash

# Python (with uv available)
podman run -it --rm container-sandbox:python python
podman run -it --rm container-sandbox:python uv --version

# Node
podman run -it --rm container-sandbox:node node

# Full-stack
podman run -it --rm container-sandbox:full-stack bash
```

### Using uv in containers
```bash
# Create a new Python project with uv (Docker)
docker run -it --rm container-sandbox:python bash -c "uv init myproject && cd myproject && uv add requests"

# Install packages with uv (Podman)
podman run -it --rm container-sandbox:python bash -c "uv pip install requests"

# Run Python with uv
docker run -it --rm container-sandbox:python bash -c "uv run python script.py"
```

### With port mapping
```bash
# Docker
docker run -it --rm -p 5173:5173 container-sandbox:python bash

# Podman
podman run -it --rm -p 5173:5173 container-sandbox:python bash
```

### With volume mounting
```bash
# Docker
docker run -it --rm -v $(pwd):/home/user/project container-sandbox:python bash

# Podman
podman run -it --rm -v $(pwd):/home/user/project container-sandbox:python bash
```

## Image Sizes

Expected sizes after build:
- Base: ~300 MB
- Python: ~800 MB
- Node: ~600 MB
- Full-Stack: ~1.2 GB

## Customization

To create a custom image, extend one of the base images:

```dockerfile
FROM container-sandbox:python

USER root
RUN apt-get update && apt-get install -y your-package
USER user

# Install additional Python packages with uv
RUN uv pip install --system your-python-package
```

## Maintenance

### Update packages
Rebuild images periodically to get security updates:

```bash
# Docker
docker build --no-cache -t container-sandbox:base ./base/

# Podman
podman build --no-cache -t container-sandbox:base ./base/
```

### Clean up old images
```bash
# Docker
docker image prune -a

# Podman
podman image prune -a
```

## Notes

- All containers run as non-root user `user` (UID 1000)
- Default working directory: `/home/user`
- Containers kept alive with `sleep infinity`
- All images based on Ubuntu 22.04 LTS
- **uv** is installed in Python and Full-Stack images for fast, reliable Python package management
