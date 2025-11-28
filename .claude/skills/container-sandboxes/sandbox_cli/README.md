# Docker Sandbox CLI - Test Suite

Comprehensive test suite for the Docker Sandbox CLI.

## Running Tests

### Prerequisites

1. **Docker images must be built:**
   ```bash
   cd ../docker
   ./build-all.sh
   ```

2. **Install test dependencies:**
   ```bash
   cd sandbox_cli
   uv pip install -e ".[dev]"
   ```

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/test_sandbox.py tests/test_commands.py tests/test_files.py

# Integration tests only
pytest tests/test_integration.py

# Quick tests (skip slow tests)
pytest -m "not slow"

# Integration tests only
pytest -m integration
```

### Run with Coverage

```bash
pytest --cov=src --cov-report=html
```

Coverage report will be in `htmlcov/index.html`.

### Run with Verbose Output

```bash
pytest -v
```

## Test Structure

```
tests/
├── __init__.py              # Test package
├── conftest.py              # Pytest fixtures and configuration
├── test_sandbox.py          # Sandbox lifecycle tests (~15 test classes)
├── test_commands.py         # Command execution tests (~10 test classes)
├── test_files.py            # File operations tests (~12 test classes)
└── test_integration.py      # Integration workflow tests (~8 test classes)
```

## Test Categories

### Unit Tests

**test_sandbox.py** - Tests for sandbox.py module:
- Creating sandboxes with various options
- Connecting to existing sandboxes
- Killing and removing sandboxes
- Listing sandboxes
- Getting sandbox information
- Pause/resume functionality
- Port mapping and host URLs

**test_commands.py** - Tests for commands.py module:
- Basic command execution
- Background command execution
- Process listing and management
- Environment variables
- Working directory changes
- User switching
- Error handling

**test_files.py** - Tests for files.py module:
- Listing files and directories
- Reading and writing text files
- Reading and writing binary files
- File operations (exists, info, remove)
- Directory operations (mkdir, rmdir)
- Renaming and moving files
- Uploading and downloading files

### Integration Tests

**test_integration.py** - End-to-end workflows:
- Complete Python development workflow
- Package installation with uv
- File manipulation workflows
- Web server workflows
- Multi-sandbox scenarios
- Data processing workflows
- Error handling

## Fixtures

Available pytest fixtures (in conftest.py):

- `docker_client` - Docker client instance
- `base_image` - Ensures base image exists
- `python_image` - Ensures Python image exists
- `sandbox` - Creates and cleans up a base sandbox
- `python_sandbox` - Creates and cleans up a Python sandbox
- `temp_file` - Creates a temporary text file
- `temp_binary_file` - Creates a temporary binary file
- `cleanup_test_containers` - Auto-cleanup after each test

## Test Markers

Custom markers for test organization:

- `@pytest.mark.slow` - Tests that take longer (>5 seconds)
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.requires_images` - Tests that require Docker images

Skip slow tests:
```bash
pytest -m "not slow"
```

Run only integration tests:
```bash
pytest -m integration
```

## Writing New Tests

### Example Unit Test

```python
import pytest
from src.modules import sandbox as sbx_module

@pytest.mark.requires_images
def test_my_feature(sandbox):
    """Test description."""
    # Test code here
    result = sbx_module.some_function(sandbox.sandbox_id)
    assert result is not None
```

### Example Integration Test

```python
import pytest
from src.modules import sandbox, commands, files

@pytest.mark.integration
@pytest.mark.requires_images
def test_my_workflow(python_sandbox):
    """Test complete workflow."""
    # Setup
    files.write_file(python_sandbox.sandbox_id, "/home/user/test.py", "print('hi')")

    # Execute
    result = commands.run_command(python_sandbox.sandbox_id, "python /home/user/test.py")

    # Verify
    assert result["exit_code"] == 0
    assert "hi" in result["stdout"]
```

## Continuous Integration

For CI/CD pipelines:

```bash
# Install dependencies
uv pip install -e ".[dev]"

# Build Docker images
cd docker && ./build-all.sh && cd ..

# Run tests with coverage
pytest --cov=src --cov-report=xml --cov-report=term

# Coverage report will be in coverage.xml
```

## Troubleshooting

### "Docker is not running"
Start Docker daemon or Docker Desktop before running tests.

### "Image not found"
Build Docker images first:
```bash
cd docker && ./build-all.sh
```

### "Containers not cleaned up"
Manually clean up test containers:
```bash
docker ps -a | grep sandbox- | awk '{print $1}' | xargs docker rm -f
```

### Slow test execution
Skip slow tests:
```bash
pytest -m "not slow"
```

Or run tests in parallel (requires pytest-xdist):
```bash
pytest -n auto
```

## Test Coverage Goals

- **Unit tests**: 80%+ coverage
- **Integration tests**: Cover major workflows
- **Edge cases**: Test error conditions

Current coverage: Run `pytest --cov=src` to see current stats.

## Contributing

When adding new features:

1. Write unit tests for the module
2. Write integration tests for the workflow
3. Ensure all tests pass: `pytest`
4. Check coverage: `pytest --cov=src`
5. Document any new fixtures or markers

---

**Total Test Count**: 100+ tests
**Test Files**: 5
**Coverage Target**: 80%+
