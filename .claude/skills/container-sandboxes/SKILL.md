---
name: Container Sandboxes
description: Operate local container sandboxes using Docker or Podman. Use when user needs to run code in isolation, test packages, execute commands safely, or work with files in a sandbox environment. No API key required. Keywords: sandbox, docker, podman, container, isolated environment, run code, test code, safe execution, local sandbox.
---

# Container Sandboxes

## Overview
Local container-based sandboxes for safe code execution. Create isolated environments for running untrusted code, testing applications, and executing commands safely using Docker or Podman containers. No API keys or external services required - everything runs locally on your machine.

## SECURITY POLICY

**CRITICAL:** Never read, write, or access files in `~/.ssh` directory (or any `.ssh` directory). This directory contains sensitive SSH keys that must not be exposed to sandboxes. For git operations, use GitHub tokens via the `GITHUB_TOKEN` environment variable instead.

## Prerequisites
- Docker or Podman installed and running
- Python 3.12+
- `uv` package manager (recommended)

## Quick Start

1. **Build the images** (first time only):
   ```bash
   cd .claude/skills/container-sandboxes/container
   ./build-all.sh
   ```
   The script auto-detects Docker or Podman. To specify:
   ```bash
   CONTAINER_RUNTIME=podman ./build-all.sh
   ```

2. **Install the CLI**:
   ```bash
   cd .claude/skills/container-sandboxes/sandbox_cli
   uv pip install -e .
   ```

3. **Initialize a sandbox**:
   ```bash
   csbx init --template container-sandbox:python
   ```
   To use a specific runtime:
   ```bash
   CONTAINER_RUNTIME=podman csbx init --template container-sandbox:python
   ```

## Core Concepts
- **Sandboxes**: Isolated containers (Docker or Podman) for safe code execution.
- **Templates**: Container images (Base, Python, Node, Full-stack).
- **Local Execution**: All code runs locally on your machine.
- **Runtime Flexibility**: Supports both Docker and Podman with auto-detection.
- **Naming**: Each sandbox gets a friendly name (e.g., `csbx-my-project`) and an ID (e.g., `abc123def456`). You can use either in commands!

## Commands Reference

### Lifecycle
- `csbx init` - Create a new sandbox (interactive or with flags)
- `csbx sandbox create` - Create a sandbox
- `csbx sandbox list` - List running sandboxes
- `csbx sandbox kill <id>` - Stop and remove a sandbox
- `csbx sandbox info <id>` - Get details about a sandbox
- `csbx sandbox get-host <id>` - Get localhost URL for a port
- `csbx sandbox export <id>` - Export sandbox files as tar.gz archive
- `csbx sandbox git-clone <id> <remote-url>` - Clone existing repository into sandbox
- `csbx sandbox git-push <id> <remote-url>` - Push sandbox code to git remote

### Execution
- `csbx exec <id> "command"` - Run a command
- `csbx exec <id> "cmd" --background` - Run in background
- `csbx exec <id> "cmd" --cwd /path` - Set working directory

### File Operations
- `csbx files ls <id> /path` - List files
- `csbx files read <id> /path` - Read file content
- `csbx files write <id> /path "content"` - Write content to file
- `csbx files upload <id> local remote` - Upload file/dir
- `csbx files download <id> remote local` - Download file/dir

## Examples

### Run Python Code
```bash
# Create sandbox with a friendly name
csbx init --template container-sandbox:python --name my-project

# Run python (using the name)
csbx exec my-project "python -c 'print(\"Hello from containers!\")'"

# Or use the ID
ID=$(csbx init --template container-sandbox:python)
csbx exec $ID "python -c 'print(\"Hello from containers!\")'"

# Cleanup (works with either name or ID)
csbx sandbox kill my-project
```

### Using Podman explicitly
```bash
CONTAINER_RUNTIME=podman csbx init --template container-sandbox:python
```

### Export Sandbox Files
```bash
# Export all files from sandbox (using name or ID)
csbx sandbox export my-project
csbx sandbox export abc123

# Export to specific directory with custom name
csbx sandbox export my-project --output ~/backups --name my-project-backup

# Export specific path only
csbx sandbox export my-project --path /home/user/myapp
```

**Important**: Sandboxes are ephemeral! Use export to save your work before the sandbox times out (default: 30 minutes).

### Clone Existing Repository

**Authentication**: Use GitHub tokens for authentication. SSH is disabled for security reasons.

```bash
# Set up GitHub token (one time)
export GITHUB_TOKEN=ghp_your_token_here

# Clone via HTTPS (using name or ID)
csbx sandbox git-clone my-project https://github.com/username/repo.git

# Clone specific branch
csbx sandbox git-clone my-project https://github.com/username/repo.git --branch dev

# Clone to specific path
csbx sandbox git-clone my-project https://github.com/username/repo.git --path /home/user/myapp

# Clone with explicit token (if not using env var)
csbx sandbox git-clone my-project https://github.com/username/repo.git --github-token $GITHUB_TOKEN
```

### Push to Git Repository

**Auto-Detection**: When you provide a GitHub/GitLab/Bitbucket URL, the command automatically clones the existing repo first, then adds your changes and pushes back. This is the most common workflow!

**Authentication**: Use GitHub tokens for authentication. SSH is disabled for security reasons.

```bash
# Set up GitHub token (one time)
export GITHUB_TOKEN=ghp_your_token_here

# Auto clone-first for GitHub repos (most common - using name or ID)
csbx sandbox git-push my-project https://github.com/username/repo.git

# Auto clone-first with custom branch
csbx sandbox git-push my-project https://github.com/username/repo.git --branch dev

# Auto clone-first with custom message
csbx sandbox git-push my-project https://github.com/username/repo.git -m "Add new feature"

# Create NEW/empty repository (skip cloning)
csbx sandbox git-push my-project https://github.com/username/new-repo.git --no-clone

# Force push (use with caution)
csbx sandbox git-push my-project https://github.com/username/repo.git --force

# Use explicit token (if not using env var)
csbx sandbox git-push my-project https://github.com/username/repo.git --github-token $GITHUB_TOKEN
```

**Setting up GitHub Token**:

**Quick method with `gh` CLI (recommended):**
```bash
# If you have gh CLI installed and authenticated
export GITHUB_TOKEN=$(gh auth token)

# Verify it's set
echo $GITHUB_TOKEN
```

**Manual method:**
```bash
# 1. Create a token at: https://github.com/settings/tokens/new
#    - Select "repo" scope for private repos, or "public_repo" for public repos only
#    - Set an appropriate expiration date

# 2. Set the token as environment variable
export GITHUB_TOKEN=ghp_your_token_here

# 3. (Optional) Add to your shell profile for persistence
echo 'export GITHUB_TOKEN=ghp_your_token_here' >> ~/.bashrc
```

**Note:** If you try to push/clone without a token, you'll get helpful instructions with the exact commands to run.

## Troubleshooting

### Container Runtime Not Running
If you see connection errors, ensure your container runtime is running:
```bash
# For Docker
docker info

# For Podman
podman info
```

Start the service if needed:
```bash
# Docker
sudo systemctl start docker

# Podman
systemctl --user start podman.socket
```

### Image Not Found
If `csbx init` fails with image not found, build the images:
```bash
cd .claude/skills/container-sandboxes/container && ./build-all.sh
```

### Switching Runtimes
To switch between Docker and Podman:
```bash
# Use Podman
export CONTAINER_RUNTIME=podman

# Use Docker
export CONTAINER_RUNTIME=docker

# Auto-detect (default)
unset CONTAINER_RUNTIME
```

## Command Reference
Quick reference for common operations:
- `csbx init` - Create a new sandbox
- `csbx exec <id> "command"` - Execute commands
- `csbx files write/read` - File operations
- Works with both Docker and Podman
