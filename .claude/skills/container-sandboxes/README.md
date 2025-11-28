# Container Sandboxes - Local Sandbox Skill

Local container-based sandboxes for AI agents and developers. Run code in isolated containers using Docker or Podman without API keys or external dependencies.

## Overview

This skill provides isolated sandbox environments for safe code execution using local containers. Perfect for:
- Local development and testing
- Offline work
- Cost savings (no API fees)
- Full control over execution environment
- **Supports both Docker and Podman runtimes**

## Quick Start

### 1. Build Container Images

```bash
cd container/
./build-all.sh
```

The script automatically detects whether you have Docker or Podman installed.

This builds 4 images:
- `container-sandbox:base` - Ubuntu 22.04 with essentials
- `container-sandbox:python` - Python 3.12 + uv
- `container-sandbox:node` - Node.js 22
- `container-sandbox:full-stack` - Python + Node + databases

To use a specific runtime:
```bash
CONTAINER_RUNTIME=docker ./build-all.sh
# or
CONTAINER_RUNTIME=podman ./build-all.sh
```

### 2. Install CLI

```bash
cd sandbox_cli/
uv pip install -e .
```

### 3. Create Your First Sandbox

```bash
# Create a sandbox (auto-detects Docker/Podman)
csbx init --template container-sandbox:python

# Output: Sandbox ID: abc123def456

# Run commands
csbx exec abc123def456 "python --version"

# Manage files
csbx files write abc123def456 /home/user/test.py "print('Hello!')"
csbx exec abc123def456 "python /home/user/test.py"

# Clean up
csbx sandbox kill abc123def456
```

To use a specific runtime:
```bash
CONTAINER_RUNTIME=podman csbx init --template container-sandbox:python
```

## Features

### Core Capabilities

| Feature | Status |
|---------|--------|
| Create sandbox | ✅ |
| Execute commands | ✅ |
| File operations | ✅ |
| Background processes | ✅ |
| Port mapping | ✅ |
| Environment variables | ✅ |
| Templates | ✅ (Container images) |
| Metadata | ✅ |
| Pause/Resume | ✅ |

### Key Advantages

| Aspect | Container Sandboxes |
|--------|---------------------|
| **Cost** | Free (local) |
| **Setup** | Docker/Podman required |
| **Network** | localhost only |
| **Speed** | Local (fast) |
| **Offline** | Yes |
| **Resource limit** | Your machine |
| **Runtime** | Docker or Podman |
| **Privacy** | Complete - never leaves your machine |

## Architecture

```
container-sandboxes/
├── container/                 # Container image definitions
│   ├── base/                  # Ubuntu base
│   ├── python/                # Python + uv
│   ├── node/                  # Node.js
│   └── full-stack/            # Combined
│
└── sandbox_cli/               # CLI implementation
    ├── src/
    │   ├── modules/           # Core logic
    │   │   ├── client.py      # Docker/Podman client
    │   │   ├── sandbox.py     # Container lifecycle
    │   │   ├── commands.py    # Command execution
    │   │   └── files.py       # File operations
    │   ├── commands/          # CLI commands
    │   │   ├── sandbox.py     # csbx sandbox *
    │   │   ├── exec.py        # csbx exec
    │   │   └── files.py       # csbx files *
    │   └── config.py          # Runtime configuration
    └── tests/                 # Test suite
```

## CLI Commands

### Sandbox Lifecycle

```bash
# Create sandbox
csbx init                                    # Quick create
csbx sandbox create --template container-sandbox:python

# List sandboxes
csbx sandbox list

# Get info
csbx sandbox info abc123

# Get public URL for port
csbx sandbox get-host abc123 --port 5173

# Kill sandbox
csbx sandbox kill abc123
```

### Command Execution

```bash
# Basic
csbx exec abc123 "python --version"

# With options
csbx exec abc123 "apt-get update" --root
csbx exec abc123 "pwd" --cwd /home/user/project
csbx exec abc123 "echo \$VAR" --env VAR=value
csbx exec abc123 "python server.py" --background

# Shell features
csbx exec abc123 "ps aux | grep python" --shell
```

### File Operations

```bash
# List
csbx files ls abc123 /home/user

# Read/Write
csbx files read abc123 /home/user/file.txt
csbx files write abc123 /home/user/file.txt "content"
echo "content" | csbx files write abc123 /home/user/file.txt --stdin

# Upload/Download
csbx files upload abc123 ./local.txt /home/user/remote.txt
csbx files download abc123 /home/user/remote.txt ./local.txt

# Directory operations
csbx files mkdir abc123 /home/user/mydir
csbx files rm abc123 /home/user/file.txt
csbx files mv abc123 /home/user/old.txt /home/user/new.txt
```

## Container Images

### Base Image
```bash
# Docker
docker run -it --rm container-sandbox:base bash
# Podman
podman run -it --rm container-sandbox:base bash
```
- Ubuntu 22.04
- Essential utilities (curl, wget, git, vim)
- Build tools
- Non-root user: `user`

### Python Image
```bash
# Docker
docker run -it --rm container-sandbox:python python
# Podman
podman run -it --rm container-sandbox:python python
```
- Everything from base
- Python 3.12
- **uv** - Fast package manager
- Common packages: flask, fastapi, numpy, pandas

### Node Image
```bash
# Docker
docker run -it --rm container-sandbox:node node
# Podman
podman run -it --rm container-sandbox:node node
```
- Everything from base
- Node.js 22 LTS
- npm, yarn, pnpm
- TypeScript, Vite, ESLint

### Full-Stack Image
```bash
# Docker
docker run -it --rm container-sandbox:full-stack bash
# Podman
podman run -it --rm container-sandbox:full-stack bash
```
- Everything from Python + Node
- Database clients: sqlite3, postgresql, redis

## Development

### Run Tests

```bash
cd sandbox_cli/
pytest
```

### Code Quality

```bash
# Format code
black src/

# Type checking
mypy src/

# Linting
flake8 src/
```

## Python API Usage

### Using in Python Code

```python
from src.modules.sandbox import ContainerSandbox
from src.modules.commands import run_command

# Create a sandbox
sbx = ContainerSandbox.create(template="container-sandbox:python")

# Run commands
result = run_command(sbx.sandbox_id, "python --version")
print(result["stdout"])

# Clean up
sbx.kill()
```

## Troubleshooting

### Container runtime not running
```
Error: Cannot connect to the container daemon
Solution: Start Docker Desktop or Podman service
  - Docker: Start Docker Desktop or run 'sudo systemctl start docker'
  - Podman: Run 'sudo systemctl start podman' or start podman socket
```

### Image not found
```
Error: No such image: container-sandbox:python
Solution: Run ./container/build-all.sh to build images
```

### Podman socket not found
```
Error: Podman socket not found
Solution: Ensure Podman socket is running:
  systemctl --user start podman.socket
Or set CONTAINER_RUNTIME=docker to use Docker instead
```

### Port already in use
```
Error: Port 5173 is already allocated
Solution: Stop other containers or use different port
```

### Permission denied
```
Error: Permission denied when writing file
Solution: Use --root flag or ensure file is in /home/user/
```

## Credits

This skill was inspired by and adapted from ideas in the [agent-sandbox-skill](https://github.com/disler/agent-sandbox-skill.git) project by disler. See [CREDITS.md](CREDITS.md) for full acknowledgments.

## Use Cases

### For AI Agents
- Execute untrusted code safely
- Test generated code in isolation
- Run complex multi-step operations
- Experiment with different environments

### For Developers
- Test code in clean environments
- Run integration tests
- Debug in isolated containers
- Prototype with different language versions

## Support

- **Documentation**: See SKILL.md and GETTING_STARTED.md
- **Implementation Details**: See IMPLEMENTATION_COMPLETE.md

---

**Status**: Phase 1 Complete ✅
- Core sandbox lifecycle ✓
- Command execution ✓
- File operations ✓
- CLI interface ✓

**Next**: Phase 2 - Testing & Documentation
