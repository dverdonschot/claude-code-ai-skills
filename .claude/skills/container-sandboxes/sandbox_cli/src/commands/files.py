"""
File operations commands.
"""

import click
from rich.console import Console
from rich.table import Table
from ..modules import files as files_module

console = Console()


@click.group()
def files():
    """File system operations."""
    pass


@files.command()
@click.argument("sandbox_id")
@click.argument("path", default="/")
@click.option("--depth", "-d", default=1, help="Directory depth to traverse")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def ls(sandbox_id, path, depth, output_json):
    """
    List files in a directory.

    Examples:
        csbx files ls abc123 /
        csbx files ls abc123 /home/user
        csbx files ls abc123 /home/user --json
    """
    try:
        if not output_json:
            console.print(f"[yellow]Listing files in {path}...[/yellow]")

        file_list = files_module.list_files(sandbox_id, path, depth)

        if output_json:
            import json
            print(json.dumps({
                "success": True,
                "path": path,
                "files": file_list,
                "count": len(file_list)
            }, indent=2))
        else:
            table = Table(title=f"Files in {path}")
            table.add_column("Type", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Size", style="yellow", justify="right")
            table.add_column("Permissions", style="dim")

            for f in file_list:
                type_icon = "📁" if f["type"] == "dir" else "📄"
                table.add_row(
                    type_icon,
                    f["name"],
                    str(f["size"]),
                    f["permissions"],
                )

            console.print(table)

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


@files.command()
@click.argument("sandbox_id")
@click.argument("path")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def read(sandbox_id, path, output_json):
    """
    Read a file.

    Examples:
        csbx files read abc123 /home/user/file.txt
        csbx files read abc123 /home/user/file.txt --json
    """
    try:
        if not output_json:
            console.print(f"[yellow]Reading {path}...[/yellow]")

        content = files_module.read_file(sandbox_id, path)

        if output_json:
            import json
            print(json.dumps({
                "success": True,
                "path": path,
                "content": content,
                "size": len(content),
                "lines": len(content.splitlines())
            }, indent=2))
        else:
            console.print(f"\n[cyan]Content of {path}:[/cyan]")
            console.print(content)

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


@files.command()
@click.argument("sandbox_id")
@click.argument("path")
@click.argument("content", required=False)
@click.option("--stdin", is_flag=True, help="Read content from stdin")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.option("--echo", is_flag=True, help="Display content after writing")
def write(sandbox_id, path, content, stdin, output_json, echo):
    """
    Write content to a file.

    Examples:
        csbx files write abc123 /home/user/file.txt "Hello World"
        echo "Hello" | csbx files write abc123 /home/user/file.txt --stdin
        csbx files write abc123 /home/user/file.txt "code" --echo
        csbx files write abc123 /home/user/file.txt "code" --json
    """
    try:
        # Read from stdin if flag is set
        if stdin:
            import sys

            content = sys.stdin.read()
        elif content is None:
            console.print("[red]✗ Error: Either provide content argument or use --stdin[/red]")
            raise click.Abort()

        if not output_json:
            console.print(f"[yellow]Writing to {path}...[/yellow]")

        info = files_module.write_file(sandbox_id, path, content)

        if output_json:
            import json
            print(json.dumps({
                "success": True,
                "path": info['path'],
                "size": len(content),
                "content": content if echo else None,
                "content_preview": content[:100] if len(content) > 100 and not echo else None
            }, indent=2))
        else:
            console.print(f"[green]✓ File written: {info['path']}[/green]")
            console.print(f"[dim]Size: {len(content)} bytes[/dim]")

            if echo:
                console.print(f"\n[cyan]Content of {path}:[/cyan]")
                console.print(content)

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


@files.command()
@click.argument("sandbox_id")
@click.argument("path")
def exists(sandbox_id, path):
    """
    Check if a file exists.

    Examples:
        csbx files exists abc123 /home/user/file.txt
    """
    try:
        exists = files_module.file_exists(sandbox_id, path)

        if exists:
            console.print(f"[green]✓ {path} exists[/green]")
        else:
            console.print(f"[red]✗ {path} does not exist[/red]")

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise click.Abort()


@files.command()
@click.argument("sandbox_id")
@click.argument("path")
def info(sandbox_id, path):
    """
    Get file information.

    Examples:
        csbx files info abc123 /home/user/file.txt
    """
    try:
        console.print(f"[yellow]Getting info for {path}...[/yellow]")

        info = files_module.get_file_info(sandbox_id, path)

        table = Table(title=f"File Info: {path}")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Name", info["name"])
        table.add_row("Path", info["path"])
        table.add_row("Type", info["type"])
        table.add_row("Size", str(info["size"]))
        table.add_row("Permissions", info["permissions"])

        console.print(table)

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise click.Abort()


@files.command()
@click.argument("sandbox_id")
@click.argument("path")
def rm(sandbox_id, path):
    """
    Remove a file or directory.

    Examples:
        csbx files rm abc123 /home/user/file.txt
    """
    try:
        console.print(f"[yellow]Removing {path}...[/yellow]")

        files_module.remove_file(sandbox_id, path)

        console.print(f"[green]✓ Removed: {path}[/green]")

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise click.Abort()


@files.command()
@click.argument("sandbox_id")
@click.argument("path")
def mkdir(sandbox_id, path):
    """
    Create a directory.

    Examples:
        csbx files mkdir abc123 /home/user/mydir
    """
    try:
        console.print(f"[yellow]Creating directory {path}...[/yellow]")

        created = files_module.make_directory(sandbox_id, path)

        if created:
            console.print(f"[green]✓ Directory created: {path}[/green]")
        else:
            console.print(f"[yellow]! Directory already exists: {path}[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise click.Abort()


@files.command()
@click.argument("sandbox_id")
@click.argument("old_path")
@click.argument("new_path")
def mv(sandbox_id, old_path, new_path):
    """
    Rename/move a file or directory.

    Examples:
        csbx files mv abc123 /home/user/old.txt /home/user/new.txt
    """
    try:
        console.print(f"[yellow]Renaming {old_path} to {new_path}...[/yellow]")

        info = files_module.rename_file(sandbox_id, old_path, new_path)

        console.print(f"[green]✓ Renamed to: {info['path']}[/green]")

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise click.Abort()


@files.command()
@click.argument("sandbox_id")
@click.argument("local_path")
@click.argument("remote_path")
def upload(sandbox_id, local_path, remote_path):
    """
    Upload a file to the sandbox.

    Examples:
        csbx files upload abc123 ./local/file.txt /home/user/file.txt
    """
    try:
        from pathlib import Path

        local_file = Path(local_path)

        if not local_file.exists():
            console.print(f"[red]✗ Local file not found: {local_path}[/red]")
            raise click.Abort()

        console.print(f"[yellow]Uploading {local_path} to {remote_path}...[/yellow]")

        info = files_module.upload_file(sandbox_id, local_path, remote_path)

        console.print(f"[green]✓ File uploaded: {info['path']}[/green]")
        console.print(f"[dim]Size: {info['size']} bytes[/dim]")

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise click.Abort()


@files.command()
@click.argument("sandbox_id")
@click.argument("remote_path")
@click.argument("local_path")
def download(sandbox_id, remote_path, local_path):
    """
    Download a file from the sandbox.

    Examples:
        csbx files download abc123 /home/user/file.txt ./local/file.txt
    """
    try:
        console.print(f"[yellow]Downloading {remote_path} to {local_path}...[/yellow]")

        info = files_module.download_file(sandbox_id, remote_path, local_path)

        console.print(f"[green]✓ File downloaded: {info['path']}[/green]")
        console.print(f"[dim]Size: {info['size']} bytes[/dim]")

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise click.Abort()
