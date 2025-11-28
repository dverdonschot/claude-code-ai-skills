"""
Sandbox lifecycle management commands.
"""

import click
from rich.console import Console
from rich.table import Table
from ..modules import sandbox as sbx_module

console = Console()


@click.group()
def sandbox():
    """Sandbox lifecycle management."""
    pass


@sandbox.command()
@click.option(
    "--template",
    "-t",
    default="docker-sandbox:base",
    help="Docker image to use",
)
@click.option("--timeout", default=1800, help="Sandbox timeout in seconds")
@click.option("--env", "-e", multiple=True, help="Environment variables (KEY=VALUE)")
@click.option("--name", "-n", default=None, help="Sandbox name")
@click.option("--port", "-p", multiple=True, help="Port mappings (container:host)")
def create(template, timeout, env, name, port):
    """
    Create a new sandbox.

    Examples:
        # Create basic sandbox
        csbx sandbox create

        # Create Python sandbox
        csbx sandbox create --template docker-sandbox:python

        # Create with port mapping
        csbx sandbox create --template docker-sandbox:python --port 5173:5173
    """
    try:
        console.print("[yellow]Creating sandbox...[/yellow]")

        # Parse env vars
        envs = {}
        for e in env:
            if "=" in e:
                key, value = e.split("=", 1)
                envs[key] = value

        # Parse port mappings
        ports = {}
        for p in port:
            if ":" in p:
                container_port, host_port = p.split(":", 1)
                ports[int(container_port)] = int(host_port)

        # Add name to metadata
        metadata = {}
        if name:
            metadata["name"] = name

        sbx = sbx_module.create_sandbox(
            template=template,
            timeout=timeout,
            envs=envs if envs else None,
            metadata=metadata if metadata else None,
            ports=ports if ports else None,
        )

        console.print(f"\n[green]✓ Sandbox created![/green]")
        console.print(f"[cyan]Sandbox ID:[/cyan] {sbx.sandbox_id}")

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise click.Abort()


@sandbox.command()
@click.argument("sandbox_id")
def kill(sandbox_id):
    """
    Kill and remove a sandbox.

    Examples:
        csbx sandbox kill abc123
    """
    try:
        console.print(f"[yellow]Killing sandbox {sandbox_id}...[/yellow]")

        result = sbx_module.kill_sandbox(sandbox_id)

        if result:
            console.print(f"[green]✓ Sandbox {sandbox_id} killed[/green]")
        else:
            console.print(f"[yellow]! Sandbox {sandbox_id} not found[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise click.Abort()


@sandbox.command()
@click.option("--limit", "-l", default=20, help="Maximum number to list")
def list(limit):
    """
    List all running sandboxes.

    Examples:
        csbx sandbox list
        csbx sandbox list --limit 10
    """
    try:
        console.print("[yellow]Listing sandboxes...[/yellow]")

        sandboxes = sbx_module.list_sandboxes(limit=limit)

        if not sandboxes:
            console.print("[yellow]No running sandboxes found[/yellow]")
            return

        table = Table(title=f"Running Sandboxes ({len(sandboxes)})")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("ID", style="dim")
        table.add_column("Template", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Started", style="dim")

        for sbx in sandboxes:
            table.add_row(
                sbx.get("name", "unknown"),
                sbx["sandbox_id"],
                sbx.get("template_id", "unknown"),
                sbx.get("status", "unknown"),
                sbx.get("started_at", "unknown"),
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise click.Abort()


@sandbox.command()
@click.argument("sandbox_id")
def info(sandbox_id):
    """
    Get sandbox information.

    Examples:
        csbx sandbox info abc123
    """
    try:
        console.print(f"[yellow]Getting info for {sandbox_id}...[/yellow]")

        info = sbx_module.get_sandbox_info(sandbox_id)

        table = Table(title=f"Sandbox Info")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Name", info.get("name", "unknown"))
        table.add_row("Sandbox ID", info["sandbox_id"])
        table.add_row("Template", info.get("template_id", "unknown"))
        table.add_row("Status", info.get("status", "unknown"))
        table.add_row("Started At", info.get("started_at", "unknown"))

        if info.get("metadata"):
            for key, value in info["metadata"].items():
                table.add_row(f"Metadata: {key}", str(value))

        console.print(table)

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise click.Abort()


@sandbox.command("get-host")
@click.argument("sandbox_id")
@click.option("--port", "-p", type=int, required=True, help="Port number")
def get_host(sandbox_id, port):
    """
    Get the public URL for an exposed port.

    Examples:
        csbx sandbox get-host abc123 --port 5173
    """
    try:
        url = sbx_module.get_host(sandbox_id, port)

        console.print(f"\n[green]Public URL:[/green]")
        console.print(f"[cyan]{url}[/cyan]")

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise click.Abort()


@sandbox.command()
@click.argument("sandbox_id")
def pause(sandbox_id):
    """
    Pause a sandbox (beta).

    Examples:
        csbx sandbox pause abc123
    """
    try:
        console.print(f"[yellow]Pausing sandbox {sandbox_id}...[/yellow]")

        sbx_module.pause_sandbox(sandbox_id)

        console.print(f"[green]✓ Sandbox {sandbox_id} paused[/green]")

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise click.Abort()


@sandbox.command()
@click.argument("sandbox_id")
def resume(sandbox_id):
    """
    Resume a paused sandbox (beta).

    Examples:
        csbx sandbox resume abc123
    """
    try:
        console.print(f"[yellow]Resuming sandbox {sandbox_id}...[/yellow]")

        sbx_module.resume_sandbox(sandbox_id)

        console.print(f"[green]✓ Sandbox {sandbox_id} resumed[/green]")

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise click.Abort()


@sandbox.command()
@click.argument("sandbox_id")
@click.option("--path", "-p", default="/home/user", help="Path to export from sandbox")
@click.option("--output", "-o", default=None, help="Output directory (default: current directory)")
@click.option("--name", "-n", default=None, help="Custom archive name (default: sandbox-{id}-{timestamp})")
def export(sandbox_id, path, output, name):
    """
    Export sandbox files as a zip archive.

    Archives all files from the specified path in the sandbox and downloads
    them to your local machine. The archive is named with the sandbox ID
    and timestamp for easy identification.

    Examples:
        # Export entire user directory
        csbx sandbox export abc123

        # Export to specific directory
        csbx sandbox export abc123 --output ~/projects

        # Export specific path with custom name
        csbx sandbox export abc123 --path /home/user/myapp --name myapp-backup
    """
    import os
    import subprocess
    from datetime import datetime

    try:
        # Generate archive name
        if name is None:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            name = f"sandbox-{sandbox_id[:8]}-{timestamp}"

        archive_name = f"{name}.tar.gz"

        # Determine output directory
        if output is None:
            output = os.getcwd()

        output_path = os.path.abspath(os.path.join(output, archive_name))

        console.print(f"[yellow]Exporting sandbox files...[/yellow]")
        console.print(f"[dim]Source: {path}[/dim]")
        console.print(f"[dim]Destination: {output_path}[/dim]")

        # Create archive inside container
        temp_archive = f"/tmp/{archive_name}"

        from ..modules import commands as cmd_module

        # Create tar archive in container
        console.print("[yellow]Creating archive in sandbox...[/yellow]")
        result = cmd_module.run_command(
            sandbox_id,
            f"tar -czf {temp_archive} -C {os.path.dirname(path)} {os.path.basename(path)}",
            timeout=300
        )

        if result["exit_code"] != 0:
            raise Exception(f"Failed to create archive: {result.get('stderr', 'Unknown error')}")

        # Copy archive to host using container runtime
        console.print("[yellow]Downloading archive to host...[/yellow]")

        from .. import config
        from ..modules.client import get_client

        client = get_client()
        container = client.containers.get(sandbox_id)

        # Get archive data (this is already a tar stream, not tar.gz)
        bits, stat = container.get_archive(temp_archive)

        # Docker's get_archive returns a tar stream of the file itself
        # We need to extract the tar.gz from it
        import tarfile
        import io

        # Collect all chunks
        tar_data = b''.join(bits)

        # Extract the tar.gz file from the tar stream
        with tarfile.open(fileobj=io.BytesIO(tar_data)) as tar:
            # Get the first member (our tar.gz file)
            member = tar.getmembers()[0]
            extracted = tar.extractfile(member)
            if extracted:
                with open(output_path, 'wb') as f:
                    f.write(extracted.read())

        # Clean up temp archive in container
        cmd_module.run_command(sandbox_id, f"rm {temp_archive}", timeout=10)

        # Get file size
        size_mb = os.path.getsize(output_path) / (1024 * 1024)

        console.print(f"\n[green]✓ Export complete![/green]")
        console.print(f"[cyan]Archive:[/cyan] {output_path}")
        console.print(f"[cyan]Size:[/cyan] {size_mb:.2f} MB")
        console.print(f"\n[dim]Extract with: tar -xzf {archive_name}[/dim]")

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise click.Abort()


@sandbox.command("git-clone")
@click.argument("sandbox_id")
@click.argument("remote_url")
@click.option("--branch", "-b", default=None, help="Branch to clone (default: main branch)")
@click.option("--path", "-p", default="/home/user", help="Path to clone into in sandbox")
@click.option("--ssh-key", "-k", default=None, help="Path to SSH key (default: ~/.claude/claude_ai_rsa)")
def git_clone(sandbox_id, remote_url, branch, path, ssh_key):
    """
    Clone a git repository into the sandbox.

    This is useful for:
    - Starting from an existing project
    - Cloning before making changes and pushing back
    - Working on an existing repository

    Supports both HTTPS and SSH authentication. For SSH, it uses a dedicated
    AI SSH key from ~/.claude/claude_ai_rsa (recommended for security).

    Examples:
        # Clone via HTTPS
        csbx sandbox git-clone my-project https://github.com/user/repo.git

        # Clone via SSH
        csbx sandbox git-clone my-project git@github.com:user/repo.git

        # Clone specific branch
        csbx sandbox git-clone my-project git@github.com:user/repo.git --branch dev

        # Clone to specific path
        csbx sandbox git-clone my-project git@github.com:user/repo.git --path /home/user/myapp
    """
    import os
    from ..modules import commands as cmd_module
    from ..modules import files as files_module

    try:
        console.print(f"[yellow]Cloning repository into sandbox...[/yellow]")
        console.print(f"[dim]Remote: {remote_url}[/dim]")
        if branch:
            console.print(f"[dim]Branch: {branch}[/dim]")

        # Determine if using SSH
        using_ssh = remote_url.startswith("git@") or remote_url.startswith("ssh://")

        # Setup SSH key if needed
        if using_ssh:
            if ssh_key is None:
                # Use AI-specific SSH key
                ssh_key = os.path.expanduser("~/.claude/claude_ai_rsa")

            if not os.path.exists(ssh_key):
                console.print(f"[red]✗ SSH key not found: {ssh_key}[/red]")
                console.print(f"\n[yellow]💡 To set up an AI-specific SSH key:[/yellow]")
                console.print(f"[dim]1. mkdir -p ~/.claude[/dim]")
                console.print(f"[dim]2. ssh-keygen -t rsa -b 4096 -f ~/.claude/claude_ai_rsa -C 'claude-ai@local'[/dim]")
                console.print(f"[dim]3. Add ~/.claude/claude_ai_rsa.pub to your GitHub/GitLab SSH keys[/dim]")
                raise click.Abort()

            console.print(f"[yellow]Setting up SSH key in sandbox...[/yellow]")

            # Create .ssh directory in sandbox
            cmd_module.run_command(sandbox_id, ["/bin/sh", "-c", "mkdir -p ~/.ssh && chmod 700 ~/.ssh"], timeout=10)

            # Copy SSH key
            with open(ssh_key, 'r') as f:
                key_content = f.read()

            files_module.write_file(sandbox_id, "~/.ssh/id_rsa", key_content.encode())
            cmd_module.run_command(sandbox_id, ["/bin/sh", "-c", "chmod 600 ~/.ssh/id_rsa"], timeout=10)

            # Copy public key if it exists
            pub_key = f"{ssh_key}.pub"
            if os.path.exists(pub_key):
                with open(pub_key, 'r') as f:
                    pub_content = f.read()
                files_module.write_file(sandbox_id, "~/.ssh/id_rsa.pub", pub_content.encode())

            # Setup SSH config to avoid host key checking (for automation)
            ssh_config = "Host *\n    StrictHostKeyChecking no\n    UserKnownHostsFile=/dev/null\n"
            files_module.write_file(sandbox_id, "~/.ssh/config", ssh_config.encode())
            cmd_module.run_command(sandbox_id, ["/bin/sh", "-c", "chmod 600 ~/.ssh/config"], timeout=10)

        # Clone the repository
        console.print("[yellow]Cloning repository...[/yellow]")

        branch_flag = f"-b {branch}" if branch else ""
        clone_cmd = f"git clone {branch_flag} {remote_url}"

        result = cmd_module.run_command(
            sandbox_id,
            ["/bin/sh", "-c", f"cd {path} && {clone_cmd}"],
            timeout=300
        )

        if result["exit_code"] != 0:
            console.print(f"[red]Clone failed:[/red]")
            console.print(result.get("stderr", "Unknown error"))
            raise click.Abort()

        console.print(f"\n[green]✓ Repository cloned successfully![/green]")
        console.print(f"[cyan]Remote:[/cyan] {remote_url}")

        if result.get("stdout"):
            console.print(f"\n[dim]{result['stdout']}[/dim]")

    except Exception as e:
        if "Abort" not in str(e):
            console.print(f"[red]✗ Error: {e}[/red]")
        raise click.Abort()


@sandbox.command("git-push")
@click.argument("sandbox_id")
@click.argument("remote_url")
@click.option("--branch", "-b", default="main", help="Branch name (default: main)")
@click.option("--path", "-p", default="/home/user", help="Path to git repository in sandbox")
@click.option("--message", "-m", default=None, help="Commit message (default: auto-generated)")
@click.option("--ssh-key", "-k", default=None, help="Path to SSH key (default: ~/.claude/claude_ai_rsa)")
@click.option("--force", "-f", is_flag=True, help="Force push")
@click.option("--no-clone", is_flag=True, help="Skip clone-first (create new repo instead)")
def git_push(sandbox_id, remote_url, branch, path, message, ssh_key, force, no_clone):
    """
    Push sandbox code to a git remote repository.

    AUTO-DETECTION: When you provide a GitHub/GitLab/Bitbucket URL, this command
    automatically uses clone-first workflow (clones the repo, adds your changes,
    and pushes back). For new/empty repositories, use --no-clone.

    This command supports two workflows:
    1. Clone-first workflow (DEFAULT for GitHub/GitLab URLs): Clone existing repo,
       add changes, commit, and push back
    2. Standard workflow: Initialize new git repo, add files, commit, and push

    The clone-first workflow is useful for:
    - Working on an existing repository
    - Pushing changes to a specific branch isolated from others
    - Continuing development on an existing project

    Supports both HTTPS and SSH authentication. For SSH, it uses a dedicated
    AI SSH key from ~/.claude/claude_ai_rsa (recommended for security).

    Examples:
        # Auto clone-first for GitHub repos (most common use case)
        csbx sandbox git-push abc123 https://github.com/user/repo.git

        # Auto clone-first with custom branch
        csbx sandbox git-push abc123 git@github.com:user/repo.git --branch dev

        # Create NEW repo (skip cloning)
        csbx sandbox git-push abc123 https://github.com/user/new-repo.git --no-clone

        # Clone-first with custom message
        csbx sandbox git-push abc123 git@github.com:user/repo.git -m "Add new feature"

        # Force push (use with caution)
        csbx sandbox git-push abc123 git@github.com:user/repo.git --force
    """
    import os
    import re
    from datetime import datetime
    from ..modules import commands as cmd_module
    from ..modules import files as files_module

    try:
        # Auto-detect if this is a GitHub/GitLab/Bitbucket URL
        # These services host existing repos, so default to clone-first
        git_hosting_patterns = [
            r'github\.com',
            r'gitlab\.com',
            r'bitbucket\.org',
            r'gitlab\.',  # Self-hosted GitLab
        ]

        is_hosted_repo = any(re.search(pattern, remote_url) for pattern in git_hosting_patterns)

        # Determine workflow: clone-first unless user explicitly says --no-clone
        clone_first = is_hosted_repo and not no_clone

        console.print(f"[yellow]Initializing git push to remote...[/yellow]")
        console.print(f"[dim]Remote: {remote_url}[/dim]")
        console.print(f"[dim]Branch: {branch}[/dim]")

        if clone_first:
            console.print(f"[dim]Mode: Clone-first workflow (auto-detected)[/dim]")
        else:
            if is_hosted_repo:
                console.print(f"[dim]Mode: New repository (--no-clone specified)[/dim]")
            else:
                console.print(f"[dim]Mode: New repository[/dim]")

        # Determine if using SSH
        using_ssh = remote_url.startswith("git@") or remote_url.startswith("ssh://")

        # Setup SSH key if needed
        if using_ssh:
            if ssh_key is None:
                # Use AI-specific SSH key
                ssh_key = os.path.expanduser("~/.claude/claude_ai_rsa")

            if not os.path.exists(ssh_key):
                console.print(f"[red]✗ SSH key not found: {ssh_key}[/red]")
                console.print(f"\n[yellow]💡 To set up an AI-specific SSH key:[/yellow]")
                console.print(f"[dim]1. mkdir -p ~/.claude[/dim]")
                console.print(f"[dim]2. ssh-keygen -t rsa -b 4096 -f ~/.claude/claude_ai_rsa -C 'claude-ai@local'[/dim]")
                console.print(f"[dim]3. Add ~/.claude/claude_ai_rsa.pub to your GitHub/GitLab SSH keys[/dim]")
                raise click.Abort()

            console.print(f"[yellow]Setting up SSH key in sandbox...[/yellow]")

            # Create .ssh directory in sandbox
            cmd_module.run_command(sandbox_id, ["/bin/sh", "-c", "mkdir -p ~/.ssh && chmod 700 ~/.ssh"], timeout=10)

            # Copy SSH key
            with open(ssh_key, 'r') as f:
                key_content = f.read()

            files_module.write_file(sandbox_id, "~/.ssh/id_rsa", key_content.encode())
            cmd_module.run_command(sandbox_id, ["/bin/sh", "-c", "chmod 600 ~/.ssh/id_rsa"], timeout=10)

            # Copy public key if it exists
            pub_key = f"{ssh_key}.pub"
            if os.path.exists(pub_key):
                with open(pub_key, 'r') as f:
                    pub_content = f.read()
                files_module.write_file(sandbox_id, "~/.ssh/id_rsa.pub", pub_content.encode())

            # Setup SSH config to avoid host key checking (for automation)
            ssh_config = "Host *\n    StrictHostKeyChecking no\n    UserKnownHostsFile=/dev/null\n"
            files_module.write_file(sandbox_id, "~/.ssh/config", ssh_config.encode())
            cmd_module.run_command(sandbox_id, ["/bin/sh", "-c", "chmod 600 ~/.ssh/config"], timeout=10)

        # Clone-first workflow
        if clone_first:
            console.print("[yellow]Cloning repository...[/yellow]")

            # Extract repo name from URL for directory name
            import re
            repo_match = re.search(r'/([^/]+?)(?:\.git)?$', remote_url)
            repo_name = repo_match.group(1) if repo_match else "repo"

            # Clone into a subdirectory
            branch_flag = f"-b {branch}" if branch else ""
            clone_cmd = f"git clone {branch_flag} {remote_url} {repo_name}"

            result = cmd_module.run_command(
                sandbox_id,
                ["/bin/sh", "-c", f"cd {path} && {clone_cmd}"],
                timeout=300
            )

            if result["exit_code"] != 0:
                console.print(f"[red]Clone failed:[/red]")
                console.print(result.get("stderr", "Unknown error"))
                raise click.Abort()

            # Update path to point to cloned repo
            path = f"{path}/{repo_name}"
            console.print(f"[green]✓ Repository cloned to {path}[/green]")

        # Configure git
        console.print("[yellow]Configuring git...[/yellow]")
        cmd_module.run_command(
            sandbox_id,
            ["/bin/sh", "-c", f"cd {path} && git config user.email 'sandbox@container.local' && git config user.name 'Container Sandbox'"],
            timeout=30
        )

        # If not clone-first, initialize git
        if not clone_first:
            console.print("[yellow]Initializing git repository...[/yellow]")
            cmd_module.run_command(
                sandbox_id,
                ["/bin/sh", "-c", f"cd {path} && git init -b {branch}"],
                timeout=30
            )

        # Add all files
        console.print("[yellow]Adding files to git...[/yellow]")
        result = cmd_module.run_command(
            sandbox_id,
            ["/bin/sh", "-c", f"cd {path} && git add -A"],
            timeout=60
        )

        if result["exit_code"] != 0:
            raise Exception(f"Failed to add files: {result.get('stderr', 'Unknown error')}")

        # Create commit
        if message is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"Sandbox changes - {timestamp}" if clone_first else f"Sandbox export - {timestamp}"

        console.print("[yellow]Creating commit...[/yellow]")
        result = cmd_module.run_command(
            sandbox_id,
            ["/bin/sh", "-c", f"cd {path} && git commit -m \"{message}\""],
            timeout=60
        )

        # Check if there were changes to commit
        if "nothing to commit" in result.get("stdout", ""):
            console.print("[yellow]No changes to commit[/yellow]")
        elif result["exit_code"] != 0:
            raise Exception(f"Failed to commit: {result.get('stderr', 'Unknown error')}")

        # Add remote if not clone-first (clone already has remote)
        if not clone_first:
            console.print("[yellow]Adding remote...[/yellow]")
            cmd_module.run_command(
                sandbox_id,
                ["/bin/sh", "-c", f"cd {path} && git remote remove origin 2>/dev/null || true"],
                timeout=30
            )

            result = cmd_module.run_command(
                sandbox_id,
                ["/bin/sh", "-c", f"cd {path} && git remote add origin {remote_url}"],
                timeout=30
            )

            if result["exit_code"] != 0:
                raise Exception(f"Failed to add remote: {result.get('stderr', 'Unknown error')}")

        # Push to remote
        force_flag = "-f" if force else ""
        console.print(f"[yellow]Pushing to {remote_url}...[/yellow]")

        result = cmd_module.run_command(
            sandbox_id,
            ["/bin/sh", "-c", f"cd {path} && git push {force_flag} -u origin {branch}"],
            timeout=300
        )

        if result["exit_code"] != 0:
            console.print(f"[red]Push failed:[/red]")
            console.print(result.get("stderr", "Unknown error"))
            raise click.Abort()

        console.print(f"\n[green]✓ Successfully pushed to remote![/green]")
        console.print(f"[cyan]Remote:[/cyan] {remote_url}")
        console.print(f"[cyan]Branch:[/cyan] {branch}")

        if result.get("stdout"):
            console.print(f"\n[dim]{result['stdout']}[/dim]")

    except Exception as e:
        if "Abort" not in str(e):
            console.print(f"[red]✗ Error: {e}[/red]")
        raise click.Abort()
