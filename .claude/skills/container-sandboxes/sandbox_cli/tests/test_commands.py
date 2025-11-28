"""
Unit tests for command execution (commands.py).
"""

import pytest
from src.modules import commands as cmd_module


@pytest.mark.requires_images
class TestRunCommand:
    """Test basic command execution."""

    def test_run_simple_command(self, sandbox):
        """Test running a simple command."""
        result = cmd_module.run_command(sandbox.sandbox_id, "echo hello")

        assert result["exit_code"] == 0
        assert "hello" in result["stdout"]
        assert result["stderr"] == ""

    def test_run_command_with_output(self, sandbox):
        """Test running a command with stdout output."""
        result = cmd_module.run_command(sandbox.sandbox_id, "ls -la /home/user")

        assert result["exit_code"] == 0
        assert len(result["stdout"]) > 0

    def test_run_command_with_error(self, sandbox):
        """Test running a command that produces stderr."""
        result = cmd_module.run_command(sandbox.sandbox_id, "ls /nonexistent")

        assert result["exit_code"] != 0
        assert len(result["stderr"]) > 0

    def test_run_command_with_cwd(self, sandbox):
        """Test running a command with custom working directory."""
        # Create a directory first
        cmd_module.run_command(sandbox.sandbox_id, "mkdir -p /home/user/testdir")

        # Run command in that directory
        result = cmd_module.run_command(
            sandbox.sandbox_id,
            "pwd",
            cwd="/home/user/testdir"
        )

        assert result["exit_code"] == 0
        assert "/home/user/testdir" in result["stdout"]

    def test_run_command_with_env_vars(self, sandbox):
        """Test running a command with environment variables."""
        result = cmd_module.run_command(
            sandbox.sandbox_id,
            "echo $TEST_VAR",
            envs={"TEST_VAR": "test_value"}
        )

        assert result["exit_code"] == 0
        assert "test_value" in result["stdout"]

    def test_run_command_as_root(self, sandbox):
        """Test running a command as root user."""
        result = cmd_module.run_command(
            sandbox.sandbox_id,
            "whoami",
            user="root"
        )

        assert result["exit_code"] == 0
        assert "root" in result["stdout"]

    def test_run_command_as_user(self, sandbox):
        """Test running a command as non-root user."""
        result = cmd_module.run_command(
            sandbox.sandbox_id,
            "whoami",
            user="user"
        )

        assert result["exit_code"] == 0
        assert "user" in result["stdout"]

    def test_run_python_command(self, python_sandbox):
        """Test running a Python command."""
        result = cmd_module.run_command(
            python_sandbox.sandbox_id,
            "python --version"
        )

        assert result["exit_code"] == 0
        assert "Python 3.12" in result["stdout"]

    def test_run_multiline_command(self, sandbox):
        """Test running a multi-line command."""
        result = cmd_module.run_command(
            sandbox.sandbox_id,
            "echo line1 && echo line2"
        )

        assert result["exit_code"] == 0
        assert "line1" in result["stdout"]
        assert "line2" in result["stdout"]


@pytest.mark.requires_images
class TestRunCommandBackground:
    """Test background command execution."""

    def test_run_background_command(self, sandbox):
        """Test running a command in background."""
        result = cmd_module.run_command_background(
            sandbox.sandbox_id,
            "sleep 10"
        )

        assert "pid" in result
        assert result["exit_code"] == -1  # Indicates still running

    def test_run_background_with_cwd(self, sandbox):
        """Test running a background command with cwd."""
        # Create directory
        cmd_module.run_command(sandbox.sandbox_id, "mkdir -p /home/user/bgtest")

        result = cmd_module.run_command_background(
            sandbox.sandbox_id,
            "sleep 5",
            cwd="/home/user/bgtest"
        )

        assert "pid" in result

    def test_run_background_with_env(self, sandbox):
        """Test running a background command with environment variables."""
        result = cmd_module.run_command_background(
            sandbox.sandbox_id,
            "sleep 5",
            envs={"BG_VAR": "bg_value"}
        )

        assert "pid" in result


@pytest.mark.requires_images
class TestListProcesses:
    """Test process listing."""

    def test_list_processes_basic(self, sandbox):
        """Test listing processes in sandbox."""
        processes = cmd_module.list_processes(sandbox.sandbox_id)

        assert isinstance(processes, list)
        assert len(processes) > 0

        # Should at least have the sleep infinity process
        commands = [p["command"] for p in processes]
        assert any("sleep" in cmd for cmd in commands)

    def test_list_processes_after_running_command(self, sandbox):
        """Test listing processes after running a background command."""
        # Run a background process
        cmd_module.run_command_background(sandbox.sandbox_id, "sleep 100")

        # List processes
        processes = cmd_module.list_processes(sandbox.sandbox_id)

        # Should see the sleep process
        commands = [p["command"] for p in processes]
        assert any("sleep 100" in cmd for cmd in commands)

    def test_process_has_expected_fields(self, sandbox):
        """Test that process info has expected fields."""
        processes = cmd_module.list_processes(sandbox.sandbox_id)

        assert len(processes) > 0
        process = processes[0]

        assert "user" in process
        assert "pid" in process
        assert "cpu" in process
        assert "mem" in process
        assert "command" in process
        assert isinstance(process["pid"], int)


@pytest.mark.requires_images
class TestKillProcess:
    """Test killing processes."""

    def test_kill_process(self, sandbox):
        """Test killing a process by PID."""
        # Start a background process
        cmd_module.run_command_background(sandbox.sandbox_id, "sleep 100")

        # Get its PID
        processes = cmd_module.list_processes(sandbox.sandbox_id)
        sleep_proc = None
        for p in processes:
            if "sleep 100" in p["command"]:
                sleep_proc = p
                break

        assert sleep_proc is not None

        # Kill it
        result = cmd_module.kill_process(sandbox.sandbox_id, sleep_proc["pid"])
        assert result is True

        # Verify it's gone (may take a moment)
        import time
        time.sleep(0.5)

        processes = cmd_module.list_processes(sandbox.sandbox_id)
        pids = [p["pid"] for p in processes]
        assert sleep_proc["pid"] not in pids

    def test_kill_nonexistent_process(self, sandbox):
        """Test killing a non-existent process."""
        # Try to kill a process that doesn't exist
        result = cmd_module.kill_process(sandbox.sandbox_id, 99999)
        # May return True or False depending on implementation
        assert isinstance(result, bool)


@pytest.mark.requires_images
class TestGetProcessStatus:
    """Test getting process status."""

    def test_get_process_status_existing(self, sandbox):
        """Test getting status of an existing process."""
        # Start a background process
        cmd_module.run_command_background(sandbox.sandbox_id, "sleep 100")

        # Get processes
        processes = cmd_module.list_processes(sandbox.sandbox_id)
        sleep_proc = None
        for p in processes:
            if "sleep 100" in p["command"]:
                sleep_proc = p
                break

        assert sleep_proc is not None

        # Get its status
        status = cmd_module.get_process_status(sandbox.sandbox_id, sleep_proc["pid"])

        assert status is not None
        assert status["pid"] == sleep_proc["pid"]
        assert "command" in status

    def test_get_process_status_nonexistent(self, sandbox):
        """Test getting status of a non-existent process."""
        status = cmd_module.get_process_status(sandbox.sandbox_id, 99999)
        assert status is None


@pytest.mark.requires_images
class TestCommandEdgeCases:
    """Test edge cases and error handling."""

    def test_run_command_empty_string(self, sandbox):
        """Test running an empty command."""
        with pytest.raises(Exception):
            cmd_module.run_command(sandbox.sandbox_id, "")

    def test_run_command_invalid_working_directory(self, sandbox):
        """Test running a command with invalid cwd."""
        result = cmd_module.run_command(
            sandbox.sandbox_id,
            "echo test",
            cwd="/nonexistent/directory"
        )

        # Should fail with non-zero exit code
        assert result["exit_code"] != 0

    def test_run_command_with_special_characters(self, sandbox):
        """Test running a command with special characters."""
        result = cmd_module.run_command(
            sandbox.sandbox_id,
            "echo 'hello \"world\" with $pecial chars'"
        )

        assert result["exit_code"] == 0

    def test_run_command_long_output(self, sandbox):
        """Test running a command with long output."""
        result = cmd_module.run_command(
            sandbox.sandbox_id,
            "seq 1 1000"
        )

        assert result["exit_code"] == 0
        assert len(result["stdout"]) > 0
        assert "1000" in result["stdout"]


@pytest.mark.requires_images
@pytest.mark.slow
class TestCommandPerformance:
    """Test command execution performance."""

    def test_multiple_commands_sequential(self, sandbox):
        """Test running multiple commands sequentially."""
        import time

        start = time.time()

        for i in range(10):
            result = cmd_module.run_command(sandbox.sandbox_id, f"echo test{i}")
            assert result["exit_code"] == 0

        duration = time.time() - start

        # Should complete in reasonable time (< 5 seconds for 10 commands)
        assert duration < 5.0

    def test_command_with_timeout(self, sandbox):
        """Test command execution respects timeout."""
        # Note: timeout not fully implemented in current version
        # This test documents expected behavior
        result = cmd_module.run_command(
            sandbox.sandbox_id,
            "sleep 1",
            timeout=2
        )

        assert result["exit_code"] == 0
