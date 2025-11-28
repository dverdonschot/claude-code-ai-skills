# Getting Started with Container Sandboxes

## What We've Built

A complete container-based sandbox system for safe local code execution. **20+ files created** implementing:

✅ **4 Container Images** (Base, Python, Node, Full-Stack)
✅ **3 Core Modules** (sandbox.py, commands.py, files.py)
✅ **3 CLI Command Groups** (sandbox, exec, files)
✅ **Complete CLI Interface** with `csbx` command
✅ **Isolated Execution Environment** for AI agents and developers
✅ **Docker and Podman Support** with auto-detection

## Installation (5 minutes)

### Step 1: Build Container Images

```bash
cd .claude/skills/container-sandboxes/container
./build-all.sh
```

The script automatically detects Docker or Podman. To specify a runtime:
```bash
CONTAINER_RUNTIME=podman ./build-all.sh
# or
CONTAINER_RUNTIME=docker ./build-all.sh
```

This creates:
- `container-sandbox:base` (~300 MB)
- `container-sandbox:python` (~800 MB) - **includes uv**
- `container-sandbox:node` (~600 MB)
- `container-sandbox:full-stack` (~1.2 GB) - **includes uv**

**Time**: ~3-5 minutes depending on internet speed

### Step 2: Install CLI

```bash
cd .claude/skills/container-sandboxes/sandbox_cli
uv pip install -e .
```

**Time**: ~30 seconds

### Step 3: Verify Installation

```bash
csbx --version
# Output: csbx, version 0.1.0

# Check images (Docker)
docker images | grep container-sandbox

# Or check images (Podman)
podman images | grep container-sandbox

# Should show 4 images
```

## First Sandbox (2 minutes)

### Example 1: Python Hello World

```bash
# 1. Create sandbox (auto-detects Docker/Podman)
SANDBOX_ID=$(csbx init --template container-sandbox:python)
echo "Sandbox: $SANDBOX_ID"

# 2. Write Python code
csbx files write $SANDBOX_ID /home/user/hello.py "print('Hello from Container Sandbox!')"

# 3. Run code
csbx exec $SANDBOX_ID "python /home/user/hello.py"
# Output: Hello from Container Sandbox!

# 4. Test uv
csbx exec $SANDBOX_ID "uv --version"
# Output: uv x.x.x

# 5. Clean up
csbx sandbox kill $SANDBOX_ID
```

### Example 2: Using Podman Explicitly

```bash
# Create sandbox with Podman
CONTAINER_RUNTIME=podman SANDBOX_ID=$(csbx init --template container-sandbox:python)

# Everything else works the same
csbx exec $SANDBOX_ID "python --version"
csbx sandbox kill $SANDBOX_ID
```

### Example 3: Web Server

```bash
# 1. Create sandbox with port mapping
csbx init --template container-sandbox:python --port 5173:5173

# Note the sandbox ID (e.g., abc123)
SANDBOX_ID=abc123

# 2. Create simple web server
csbx files write $SANDBOX_ID /home/user/server.py "
from http.server import HTTPServer, SimpleHTTPRequestHandler

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'<h1>Hello from Container Sandbox!</h1>')

httpd = HTTPServer(('0.0.0.0', 5173), Handler)
print('Server running on port 5173')
httpd.serve_forever()
"

# 3. Start server in background
csbx exec $SANDBOX_ID "python /home/user/server.py" --background

# 4. Get URL
csbx sandbox get-host $SANDBOX_ID --port 5173
# Output: http://localhost:5173

# 5. Visit http://localhost:5173 in your browser
# You should see: "Hello from Container Sandbox!"

# 6. Clean up
csbx sandbox kill $SANDBOX_ID
```

### Example 3: Full-Stack Development

```bash
# 1. Create full-stack sandbox
SANDBOX_ID=$(csbx init --template container-sandbox:full-stack --port 5173:5173)

# 2. Test Python
csbx exec $SANDBOX_ID "python --version"
# Output: Python 3.12.x

# 3. Test uv
csbx exec $SANDBOX_ID "uv --version"
# Output: uv x.x.x

# 4. Test Node
csbx exec $SANDBOX_ID "node --version"
# Output: v22.x.x

# 5. Install Python package with uv
csbx exec $SANDBOX_ID "uv pip install --system requests"

# 6. Install Node package
csbx exec $SANDBOX_ID "npm install -g cowsay"

# 7. Test installations
csbx exec $SANDBOX_ID "python -c 'import requests; print(requests.__version__)'"
csbx exec $SANDBOX_ID "cowsay 'Container Sandboxes Rock!'"

# 8. Clean up
csbx sandbox kill $SANDBOX_ID
```

## Common Workflows

### Python Package Testing

```bash
# Create Python sandbox
SANDBOX_ID=$(csbx init --template container-sandbox:python)

# Install package with uv (fast!)
csbx exec $SANDBOX_ID "uv pip install --system numpy pandas"

# Test package
csbx files write $SANDBOX_ID /home/user/test.py "
import numpy as np
import pandas as pd
print('NumPy version:', np.__version__)
print('Pandas version:', pd.__version__)
"

csbx exec $SANDBOX_ID "python /home/user/test.py"

# Clean up
csbx sandbox kill $SANDBOX_ID
```

### Node.js Project Testing

```bash
# Create Node sandbox
SANDBOX_ID=$(csbx init --template container-sandbox:node)

# Create package.json
csbx files write $SANDBOX_ID /home/user/package.json '{
  "name": "test-project",
  "version": "1.0.0",
  "type": "module",
  "dependencies": {
    "chalk": "^5.3.0"
  }
}'

# Install dependencies
csbx exec $SANDBOX_ID "npm install" --cwd /home/user

# Create script
csbx files write $SANDBOX_ID /home/user/index.js "
import chalk from 'chalk';
console.log(chalk.blue('Hello from Container Sandbox!'));
"

# Run script
csbx exec $SANDBOX_ID "node index.js" --cwd /home/user

# Clean up
csbx sandbox kill $SANDBOX_ID
```

### File Upload/Download

```bash
# Create sandbox
SANDBOX_ID=$(csbx init --template container-sandbox:python)

# Upload local file
echo "Local content" > /tmp/local.txt
csbx files upload $SANDBOX_ID /tmp/local.txt /home/user/remote.txt

# Process file in sandbox
csbx exec $SANDBOX_ID "cat /home/user/remote.txt | tr '[:lower:]' '[:upper:]' > /home/user/processed.txt"

# Download result
csbx files download $SANDBOX_ID /home/user/processed.txt /tmp/result.txt
cat /tmp/result.txt
# Output: LOCAL CONTENT

# Clean up
csbx sandbox kill $SANDBOX_ID
rm /tmp/local.txt /tmp/result.txt
```

## Key Commands Reference

### Sandbox Management

```bash
csbx init                                    # Quick create
csbx sandbox create --template IMAGE        # Create with template
csbx sandbox list                            # List all sandboxes
csbx sandbox info SANDBOX_ID                 # Get sandbox details
csbx sandbox get-host SANDBOX_ID --port PORT # Get URL for port
csbx sandbox kill SANDBOX_ID                 # Stop and remove
```

### Command Execution

```bash
csbx exec SANDBOX_ID "command"               # Basic execution
csbx exec SANDBOX_ID "command" --root        # Run as root
csbx exec SANDBOX_ID "command" --cwd /path   # Set working directory
csbx exec SANDBOX_ID "command" --env KEY=VAL # Set environment variable
csbx exec SANDBOX_ID "command" --background  # Run in background
csbx exec SANDBOX_ID "cmd" --shell           # Enable pipes/redirections
```

### File Operations

```bash
csbx files ls SANDBOX_ID /path               # List files
csbx files read SANDBOX_ID /path/file        # Read file
csbx files write SANDBOX_ID /path "content"  # Write file
csbx files mkdir SANDBOX_ID /path            # Create directory
csbx files rm SANDBOX_ID /path               # Remove file/directory
csbx files mv SANDBOX_ID /old /new           # Rename/move
csbx files upload SANDBOX_ID local remote    # Upload file
csbx files download SANDBOX_ID remote local  # Download file
```

## Tips & Best Practices

### 1. Use Templates Wisely

- `container-sandbox:base` - Minimal, fast startup
- `container-sandbox:python` - Python projects (**includes uv**)
- `container-sandbox:node` - JavaScript/TypeScript projects
- `container-sandbox:full-stack` - Mixed or complex projects (**includes uv**)

### 2. Port Mapping

Always map ports when creating if you'll run servers:
```bash
csbx init --template container-sandbox:python --port 5173:5173 --port 8000:8000
```

### 3. Background Processes

For long-running servers:
```bash
csbx exec $SANDBOX_ID "python server.py" --background --timeout 0
```

### 4. File Writing with Special Characters

For complex file content, use stdin:
```bash
cat << 'EOF' | csbx files write $SANDBOX_ID /home/user/file.js --stdin
const arr = [1, 2, 3];
const obj = {"key": "value"};
EOF
```

### 5. Use uv for Python Packages

The Python and Full-Stack images include **uv** for fast package management:
```bash
# Much faster than pip!
csbx exec $SANDBOX_ID "uv pip install --system numpy pandas matplotlib"

# Create virtual environment with uv
csbx exec $SANDBOX_ID "uv venv /home/user/venv"
csbx exec $SANDBOX_ID "source /home/user/venv/bin/activate && uv pip install requests" --shell
```

### 6. Clean Up Regularly

List and kill unused sandboxes:
```bash
csbx sandbox list
csbx sandbox kill OLD_SANDBOX_ID
```

Or kill all (Docker):
```bash
docker ps | grep sandbox- | awk '{print $1}' | xargs docker stop
docker ps -a | grep sandbox- | awk '{print $1}' | xargs docker rm
```

Or kill all (Podman):
```bash
podman ps | grep sandbox- | awk '{print $1}' | xargs podman stop
podman ps -a | grep sandbox- | awk '{print $1}' | xargs podman rm
```

## Troubleshooting

### Issue: "Cannot connect to container daemon"
**Solution**: Start your container runtime:

For Docker:
```bash
# Linux
sudo systemctl start docker

# macOS/Windows
# Start Docker Desktop application
```

For Podman:
```bash
# Linux
systemctl --user start podman.socket
sudo systemctl start podman  # for system-level
```

### Issue: "No such image: container-sandbox:python"
**Solution**: Build the images first:
```bash
cd container/
./build-all.sh
```

### Issue: Port already in use
**Solution**: Either:
1. Use a different port: `--port 5174:5174`
2. Kill the process using the port
3. Use auto-port allocation (not implemented yet)

### Issue: Permission denied in container
**Solution**: Run as root for system operations:
```bash
csbx exec $SANDBOX_ID "apt-get update" --root
```

## Runtime Selection

You can control which container runtime to use:

```bash
# Auto-detect (default) - prefers Podman, falls back to Docker
csbx init --template container-sandbox:python

# Explicitly use Docker
CONTAINER_RUNTIME=docker csbx init --template container-sandbox:python

# Explicitly use Podman
CONTAINER_RUNTIME=podman csbx init --template container-sandbox:python

# Set globally for your session
export CONTAINER_RUNTIME=podman
csbx init --template container-sandbox:python
```

## Next Steps

1. **Read the full docs**: See `README.md` for comprehensive documentation
2. **Check implementation details**: See `IMPLEMENTATION_COMPLETE.md`
3. **Browse examples**: See `examples/` directory
4. **Run tests**: `cd sandbox_cli && pytest`

## What's Working Right Now

✅ Sandbox creation and lifecycle
✅ Command execution (foreground/background)
✅ File operations (read/write/upload/download)
✅ Port mapping
✅ Environment variables
✅ Metadata and labels
✅ Multiple templates
✅ **uv package manager** in Python images

## What's Next (Future Development)

- [ ] Browser automation integration
- [ ] Comprehensive test suite
- [ ] Example files for common workflows
- [ ] Auto-timeout implementation
- [ ] Image management commands
- [ ] Better error messages
- [ ] Performance optimization

## Success!

You now have a fully functional local sandbox system. Try the examples above and explore the capabilities!

**Questions or issues?** Check the `README.md` or `DOCKER_SANDBOX_IMPLEMENTATION_PLAN.md` for more details.

---

**Built**: 2025-11-26
**Version**: 0.1.0 (Phase 1 Complete)
**Status**: Ready for testing ✅
