"""
Container Sandbox CLI - Main entry point.

Local container-based sandboxes for safe code execution.
"""

import click
from rich.console import Console
from . import config

# Import command groups
from .commands.sandbox import sandbox
from .commands.files import files
from .commands.exec import exec
from .commands.browser import browser

console = Console()


@click.group()
@click.version_option(version="0.1.0")
@click.option("--podman", is_flag=True, help="Use Podman instead of Docker")
def cli(podman):
    """
    Docker Sandbox CLI - Control local sandboxes from the command line.

    This CLI provides comprehensive sandbox management using Docker:
    - Create, connect to, and manage sandboxes (sandbox)
    - Perform file operations with Docker APIs (files)
    - Execute any command with full control (exec)

    Most commands require a SANDBOX_ID. You can get one by:
    1. Creating a new sandbox: csbx init
    2. Or: csbx sandbox create

    Tip: Store your sandbox ID for easier use:
      SANDBOX_ID=$(csbx init)
      csbx files ls $SANDBOX_ID /
      csbx exec $SANDBOX_ID "python --version"

    Requirements:
    - Docker (or Podman) must be installed and running
    - Docker images must be built (see docker/ directory)
    """
    if podman:
        config.USE_PODMAN = True



# Add command groups
cli.add_command(sandbox)
cli.add_command(files)
cli.add_command(exec)
cli.add_command(browser)


# Add an init command for quick sandbox setup
@cli.command()
@click.option(
    "--template",
    "-t",
    default="docker-sandbox:base",
    help="Docker image to use (default: docker-sandbox:base)",
)
@click.option(
    "--timeout", default=1800, help="Sandbox timeout in seconds (default: 30 minutes)"
)
@click.option("--env", "-e", multiple=True, help="Environment variables (KEY=VALUE)")
@click.option("--name", "-n", default=None, help="Container name (e.g., my-project)")
@click.option("--port", "-p", multiple=True, help="Port mappings (container:host)")
@click.option("--mount", "-m", multiple=True, help="Volume mounts (host_path:container_path or host_path:container_path:mode)")
def init(template, timeout, env, name, port, mount):
    """
    Initialize a new sandbox and display the ID.

    This is a convenience command that creates a sandbox and
    displays the ID and name for use in other commands.

    Templates:
        You can create a sandbox from different Docker images.
        Available templates:
        - docker-sandbox:base (minimal Ubuntu)
        - docker-sandbox:python (Python 3.12 + uv)
        - docker-sandbox:node (Node.js 22)
        - docker-sandbox:full-stack (Python + Node)

    Examples:
        # Create with default base template
        csbx init

        # Create with Python template and custom name
        csbx init --template docker-sandbox:python --name my-project

        # Create with environment variables
        csbx init --template docker-sandbox:python --env API_KEY=secret

        # Create with port mapping
        csbx init --template docker-sandbox:python --port 5173:5173 --name notes-app

        # Create with volume mount (live file editing!)
        csbx init --template docker-sandbox:deno --mount ~/my-project:/home/user/app --name deno-dev

        # Multiple volume mounts with read-only mode
        csbx init --template docker-sandbox:python --mount ~/code:/home/user/code --mount ~/data:/home/user/data:ro
    """
    try:
        from .modules import sandbox as sbx_module

        console.print("[yellow]Initializing new sandbox...[/yellow]")
        console.print(f"[dim]Template: {template}[/dim]")

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

        # Parse volume mounts
        import os
        volumes = {}
        for m in mount:
            parts = m.split(":")
            if len(parts) >= 2:
                host_path = os.path.abspath(os.path.expanduser(parts[0]))
                container_path = parts[1]
                # Support mode with optional SELinux flags: ro, rw, z, Z, ro,z, rw,Z, etc.
                mode = parts[2] if len(parts) > 2 else "rw,Z"  # Default to rw with SELinux relabeling
                volumes[host_path] = {"bind": container_path, "mode": mode}

        sbx = sbx_module.create_sandbox(
            template=template,
            timeout=timeout,
            envs=envs if envs else None,
            ports=ports if ports else None,
            name=name,
            volumes=volumes if volumes else None,
        )

        console.print(f"\n[green]✓ Sandbox created successfully![/green]")
        console.print(f"\n[cyan]Container Name:[/cyan] {sbx.name}")
        console.print(f"[cyan]Sandbox ID:[/cyan] {sbx.sandbox_id}")
        console.print(f"[dim]Template: {template}[/dim]")
        console.print(f"\n[dim]💡 You can use either the name or ID in commands:[/dim]")
        console.print(f"[dim]   csbx exec {sbx.name} \"command\"[/dim]")
        console.print(f"[dim]   csbx exec {sbx.sandbox_id} \"command\"[/dim]")

        if ports:
            console.print(f"\n[cyan]Port mappings:[/cyan]")
            for container_port, host_port in ports.items():
                console.print(f"  {container_port} → {host_port}")

        if volumes:
            console.print(f"\n[cyan]Volume mounts:[/cyan]")
            for host_path, mount_info in volumes.items():
                mode_str = f" ({mount_info['mode']})" if mount_info.get('mode') != 'rw' else ''
                console.print(f"  {host_path} → {mount_info['bind']}{mode_str}")

        console.print(f"\n[dim]Timeout: {timeout} seconds (~{timeout // 60} minutes)[/dim]")

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise click.Abort()


if __name__ == "__main__":
    cli()
