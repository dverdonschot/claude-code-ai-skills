"""
Command execution module for Docker sandboxes.

Provides helper functions for running commands inside containers.
"""

from typing import Optional, Dict, List, Any
import docker
from docker.models.containers import Container
from .client import get_client


def run_command(
    sandbox_id: str,
    cmd: str,
    cwd: Optional[str] = None,
    envs: Optional[Dict[str, str]] = None,
    timeout: Optional[float] = 60,
    user: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run a command in the sandbox and wait for it to complete.

    Args:
        sandbox_id: Container ID
        cmd: Command to execute
        cwd: Working directory
        envs: Environment variables
        timeout: Command timeout in seconds
        user: User to run as (e.g., 'user', 'root')

    Returns:
        Dictionary with stdout, stderr, exit_code
    """
    client = get_client()
    container = client.containers.get(sandbox_id)

    # Prepare exec_run parameters
    exec_params: Dict[str, Any] = {
        "cmd": cmd,
        "stdout": True,
        "stderr": True,
        "demux": True,
    }

    if cwd:
        exec_params["workdir"] = cwd

    if envs:
        exec_params["environment"] = envs

    if user:
        exec_params["user"] = user

    # Execute command
    result = container.exec_run(**exec_params)

    # Process output
    stdout = ""
    stderr = ""

    if result.output:
        if isinstance(result.output, tuple):
            # demux=True returns (stdout, stderr)
            stdout_bytes, stderr_bytes = result.output
            stdout = stdout_bytes.decode("utf-8") if stdout_bytes else ""
            stderr = stderr_bytes.decode("utf-8") if stderr_bytes else ""
        else:
            # demux=False returns combined output
            stdout = result.output.decode("utf-8") if result.output else ""

    return {
        "stdout": stdout,
        "stderr": stderr,
        "exit_code": result.exit_code,
    }


def run_command_background(
    sandbox_id: str,
    cmd: str,
    cwd: Optional[str] = None,
    envs: Optional[Dict[str, str]] = None,
    timeout: Optional[float] = None,
    user: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run a command in the background and return immediately.

    Args:
        sandbox_id: Container ID
        cmd: Command to execute
        cwd: Working directory
        envs: Environment variables
        timeout: Command timeout (not used for background)
        user: User to run as

    Returns:
        Dictionary with exec_id (process starts immediately, does not wait)
    """
    client = get_client()
    container = client.containers.get(sandbox_id)

    # Prepare exec_run parameters
    exec_params: Dict[str, Any] = {
        "cmd": cmd,
        "stdout": True,
        "stderr": True,
        "detach": True,  # Run in background
    }

    if cwd:
        exec_params["workdir"] = cwd

    if envs:
        exec_params["environment"] = envs

    if user:
        exec_params["user"] = user

    # Execute command in background
    exec_instance = container.exec_run(**exec_params)

    # For detached execution, exec_run returns an ExecResult
    # We'll use a simple approach: return the command as reference
    return {
        "pid": "background",  # Placeholder since we can't get real PID easily
        "stdout": "",
        "stderr": "",
        "exit_code": -1,  # -1 indicates process is still running
    }


def list_processes(sandbox_id: str) -> List[Dict[str, Any]]:
    """
    List all running processes in the sandbox.

    Args:
        sandbox_id: Container ID

    Returns:
        List of process info dictionaries
    """
    # Use ps command to list processes
    result = run_command(sandbox_id, "ps aux", user="root")

    if result["exit_code"] != 0:
        return []

    # Parse ps output
    processes = []
    lines = result["stdout"].strip().split("\n")

    # Skip header line
    for line in lines[1:]:
        parts = line.split(None, 10)
        if len(parts) >= 11:
            processes.append(
                {
                    "user": parts[0],
                    "pid": int(parts[1]),
                    "cpu": parts[2],
                    "mem": parts[3],
                    "command": parts[10],
                }
            )

    return processes


def kill_process(sandbox_id: str, pid: int) -> bool:
    """
    Kill a process by PID.

    Args:
        sandbox_id: Container ID
        pid: Process ID to kill

    Returns:
        True if killed successfully, False otherwise
    """
    result = run_command(sandbox_id, f"kill {pid}", user="root")
    return result["exit_code"] == 0


def get_process_status(sandbox_id: str, pid: int) -> Optional[Dict[str, Any]]:
    """
    Get status of a specific process.

    Args:
        sandbox_id: Container ID
        pid: Process ID

    Returns:
        Process info dictionary or None if not found
    """
    processes = list_processes(sandbox_id)

    for proc in processes:
        if proc["pid"] == pid:
            return proc

    return None
