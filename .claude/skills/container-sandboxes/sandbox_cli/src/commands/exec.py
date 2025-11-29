"""
Advanced command execution with full Docker control.
"""

import click
from rich.console import Console
from ..modules import commands as cmd_module

console = Console()


@click.command()
@click.argument("sandbox_id")
@click.argument("command")
@click.option("--cwd", default=None, help="Working directory")
@click.option("--user", default=None, help="Run as specific user (e.g., 'user', 'root')")
@click.option("--root", is_flag=True, help="Run as root user (shortcut for --user root)")
@click.option(
    "--shell", is_flag=True, help="Execute in shell context (enables pipes, redirections)"
)
@click.option("--env", "-e", multiple=True, help="Environment variables (KEY=VALUE)")
@click.option("--timeout", default=60, type=int, help="Command timeout in seconds (0 for unlimited)")
@click.option("--background", is_flag=True, help="Run in background")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.option("--echo", is_flag=True, help="Always display full output (stdout/stderr)")
def exec(sandbox_id, command, cwd, user, root, shell, env, timeout, background, output_json, echo):
    r"""
    Execute a command with full control over execution environment.

    This is the most powerful command execution tool, supporting:
    - Custom working directory (--cwd)
    - User selection (--user or --root flag)
    - Shell context for pipes/redirections (--shell)
    - Environment variables (--env)
    - Background execution (--background)
    - Timeout control (--timeout)

    Examples:
        # Basic execution
        csbx exec abc123 "python --version"

        # Run as root
        csbx exec abc123 "apt-get update" --root

        # With custom environment
        csbx exec abc123 "echo \$VAR" --env VAR=value

        # In specific directory
        csbx exec abc123 "pwd" --cwd /home/user/project

        # Shell features (pipes, redirections)
        csbx exec abc123 "ps aux | grep python" --shell

        # Background with no timeout
        csbx exec abc123 "python server.py" --background --timeout 0

        # Complex privileged operation
        csbx exec abc123 "apt-get update && apt-get install -y nginx" --root --timeout 300
    """
    try:
        # Handle --root flag
        if root:
            user = "root"

        # Parse env vars
        envs = {}
        for e in env:
            if "=" in e:
                key, value = e.split("=", 1)
                envs[key] = value

        # Wrap in shell if requested
        actual_command = command
        if shell:
            actual_command = f'/bin/bash -c "{command}"'
            if not output_json:
                console.print(f"[yellow]Executing shell command: {command}[/yellow]")
        else:
            if not output_json:
                console.print(f"[yellow]Executing: {command}[/yellow]")

        if not output_json:
            if user:
                console.print(f"[dim]User: {user}[/dim]")
            if cwd:
                console.print(f"[dim]Working directory: {cwd}[/dim]")
            if envs:
                console.print(
                    f"[dim]Environment: {', '.join(f'{k}={v}' for k, v in envs.items())}[/dim]"
                )

        if background:
            result = cmd_module.run_command_background(
                sandbox_id,
                actual_command,
                cwd=cwd,
                envs=envs if envs else None,
                timeout=timeout if timeout > 0 else None,
                user=user,
            )
            if output_json:
                import json
                print(json.dumps({
                    "success": True,
                    "background": True,
                    "message": "Command started in background"
                }, indent=2))
            else:
                console.print(f"\n[green]✓ Background command started[/green]")
                console.print(f"[dim]Process is running in background[/dim]")
            return  # Exit early for background commands
        else:
            result = cmd_module.run_command(
                sandbox_id,
                actual_command,
                cwd=cwd,
                envs=envs if envs else None,
                timeout=timeout if timeout > 0 else None,
                user=user,
            )

        if output_json:
            import json
            print(json.dumps({
                "success": result['exit_code'] == 0,
                "exit_code": result['exit_code'],
                "stdout": result["stdout"],
                "stderr": result["stderr"],
                "command": command,
                "cwd": cwd,
                "user": user
            }, indent=2))
        else:
            console.print(f"\n[cyan]Exit code: {result['exit_code']}[/cyan]")

            # With --echo, always show output; without it, show as before
            if echo or result["stdout"]:
                if result["stdout"]:
                    console.print("\n[green]STDOUT:[/green]")
                    console.print(result["stdout"])
                elif echo:
                    console.print("\n[dim]No stdout output[/dim]")

            if echo or result["stderr"]:
                if result["stderr"]:
                    console.print("\n[red]STDERR:[/red]")
                    console.print(result["stderr"])
                elif echo:
                    console.print("\n[dim]No stderr output[/dim]")

    except Exception as e:
        if output_json:
            import json
            print(json.dumps({
                "success": False,
                "error": str(e)
            }))
        else:
            console.print(f"[red]✗ Error: {e}[/red]")
        raise click.Abort()
