"""
File operations module for Docker sandboxes.

Provides helper functions for file management inside containers.
"""

from typing import List, Dict, Any
from pathlib import Path
import tarfile
import io
import docker
from .commands import run_command
from .client import get_client


def list_files(sandbox_id: str, path: str = "/", depth: int = 1) -> List[Dict[str, Any]]:
    """
    List files in a directory.

    Args:
        sandbox_id: Container ID
        path: Path to list
        depth: Depth to traverse (not fully implemented, shows one level)

    Returns:
        List of file info dictionaries
    """
    # Use ls -la to get file information
    cmd = f"ls -la --time-style=full-iso '{path}'"
    result = run_command(sandbox_id, cmd)

    if result["exit_code"] != 0:
        raise FileNotFoundError(f"Path not found: {path}")

    files = []
    lines = result["stdout"].strip().split("\n")

    # Skip first line (total) and process file listings
    for line in lines[1:]:
        if not line.strip():
            continue

        parts = line.split(None, 8)
        if len(parts) < 9:
            continue

        permissions = parts[0]
        size = int(parts[4]) if parts[4].isdigit() else 0
        name = parts[8]

        # Skip . and ..
        if name in [".", ".."]:
            continue

        # Determine type
        file_type = "dir" if permissions.startswith("d") else "file"

        files.append(
            {
                "name": name,
                "path": f"{path.rstrip('/')}/{name}",
                "type": file_type,
                "size": size,
                "permissions": permissions,
            }
        )

    return files


def read_file(sandbox_id: str, path: str) -> str:
    """
    Read a file from the sandbox.

    Args:
        sandbox_id: Container ID
        path: Path to the file

    Returns:
        File content as string
    """
    result = run_command(sandbox_id, f"cat '{path}'")

    if result["exit_code"] != 0:
        raise FileNotFoundError(f"File not found or cannot read: {path}")

    return result["stdout"]


def read_file_bytes(sandbox_id: str, path: str) -> bytearray:
    """
    Read a file as binary data from the sandbox.

    Args:
        sandbox_id: Container ID
        path: Path to the file

    Returns:
        File content as bytearray
    """
    client = get_client()
    container = client.containers.get(sandbox_id)

    # Use get_archive to retrieve file as tar
    try:
        bits, stat = container.get_archive(path)
    except Exception as e:
        raise FileNotFoundError(f"File not found: {path}") from e

    # Extract file from tar archive
    file_data = io.BytesIO()
    for chunk in bits:
        file_data.write(chunk)
    file_data.seek(0)

    # Open tar and extract file content
    with tarfile.open(fileobj=file_data) as tar:
        members = tar.getmembers()
        if members:
            file_member = members[0]
            extracted = tar.extractfile(file_member)
            if extracted:
                return bytearray(extracted.read())

    raise FileNotFoundError(f"Could not extract file: {path}")


def write_file(sandbox_id: str, path: str, content: str) -> Dict[str, Any]:
    """
    Write a file to the sandbox.

    Args:
        sandbox_id: Container ID
        path: Path to write to
        content: Content to write

    Returns:
        Write info dictionary
    """
    # Escape single quotes in content
    escaped_content = content.replace("'", "'\"'\"'")

    # Use printf for better handling of special characters
    cmd = f"printf '%s' '{escaped_content}' > '{path}'"
    result = run_command(sandbox_id, cmd, user="user")

    if result["exit_code"] != 0:
        raise IOError(f"Failed to write file: {path}\n{result['stderr']}")

    return {"path": path}


def write_file_bytes(sandbox_id: str, path: str, data: bytes) -> Dict[str, Any]:
    """
    Write binary data to a file in the sandbox.

    Args:
        sandbox_id: Container ID
        path: Path to write to
        data: Binary data to write

    Returns:
        Write info dictionary
    """
    client = docker.from_env()
    container = client.containers.get(sandbox_id)

    # Create tar archive with the file
    file_name = Path(path).name
    file_dir = str(Path(path).parent)

    tar_stream = io.BytesIO()
    with tarfile.open(fileobj=tar_stream, mode="w") as tar:
        tarinfo = tarfile.TarInfo(name=file_name)
        tarinfo.size = len(data)
        tar.addfile(tarinfo, io.BytesIO(data))

    tar_stream.seek(0)

    # Upload to container
    container.put_archive(file_dir, tar_stream)

    return {"path": path}


def file_exists(sandbox_id: str, path: str) -> bool:
    """
    Check if a file or directory exists.

    Args:
        sandbox_id: Container ID
        path: Path to check

    Returns:
        True if exists, False otherwise
    """
    result = run_command(sandbox_id, f"test -e '{path}'")
    return result["exit_code"] == 0


def get_file_info(sandbox_id: str, path: str) -> Dict[str, Any]:
    """
    Get information about a file or directory.

    Args:
        sandbox_id: Container ID
        path: Path to get info for

    Returns:
        File info dictionary
    """
    # Use stat command to get detailed info
    cmd = f"stat -c '%n|%s|%F|%a' '{path}'"
    result = run_command(sandbox_id, cmd)

    if result["exit_code"] != 0:
        raise FileNotFoundError(f"File not found: {path}")

    # Parse stat output: name|size|type|permissions
    parts = result["stdout"].strip().split("|")

    file_type = "file"
    if "directory" in parts[2].lower():
        file_type = "dir"

    return {
        "name": Path(path).name,
        "path": path,
        "type": file_type,
        "size": int(parts[1]),
        "permissions": parts[3],
    }


def remove_file(sandbox_id: str, path: str) -> None:
    """
    Remove a file or directory.

    Args:
        sandbox_id: Container ID
        path: Path to remove
    """
    result = run_command(sandbox_id, f"rm -rf '{path}'")

    if result["exit_code"] != 0:
        raise IOError(f"Failed to remove: {path}\n{result['stderr']}")


def make_directory(sandbox_id: str, path: str) -> bool:
    """
    Create a directory.

    Args:
        sandbox_id: Container ID
        path: Path to create

    Returns:
        True if created, False if already exists
    """
    # Check if already exists
    if file_exists(sandbox_id, path):
        return False

    result = run_command(sandbox_id, f"mkdir -p '{path}'")

    if result["exit_code"] != 0:
        raise IOError(f"Failed to create directory: {path}\n{result['stderr']}")

    return True


def rename_file(sandbox_id: str, old_path: str, new_path: str) -> Dict[str, Any]:
    """
    Rename a file or directory.

    Args:
        sandbox_id: Container ID
        old_path: Current path
        new_path: New path

    Returns:
        Info about renamed file
    """
    result = run_command(sandbox_id, f"mv '{old_path}' '{new_path}'")

    if result["exit_code"] != 0:
        raise IOError(f"Failed to rename: {old_path} → {new_path}\n{result['stderr']}")

    return get_file_info(sandbox_id, new_path)


def upload_file(sandbox_id: str, local_path: str, remote_path: str) -> Dict[str, Any]:
    """
    Upload a file from local filesystem to sandbox.

    Args:
        sandbox_id: Container ID
        local_path: Local file path
        remote_path: Destination path in sandbox

    Returns:
        Upload info dictionary
    """
    local_file = Path(local_path)

    if not local_file.exists():
        raise FileNotFoundError(f"Local file not found: {local_path}")

    # Read local file
    data = local_file.read_bytes()

    # Write to sandbox using tar
    write_file_bytes(sandbox_id, remote_path, data)

    return {
        "path": remote_path,
        "size": len(data),
    }


def download_file(sandbox_id: str, remote_path: str, local_path: str) -> Dict[str, Any]:
    """
    Download a file from sandbox to local filesystem.

    Args:
        sandbox_id: Container ID
        remote_path: Source path in sandbox
        local_path: Destination path on local filesystem

    Returns:
        Download info dictionary
    """
    # Read from sandbox
    data = read_file_bytes(sandbox_id, remote_path)

    # Write to local file
    local_file = Path(local_path)
    local_file.parent.mkdir(parents=True, exist_ok=True)
    local_file.write_bytes(data)

    return {
        "path": local_path,
        "size": len(data),
    }
