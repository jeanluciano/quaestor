"""Update command for Quaestor."""

from pathlib import Path

import typer
from rich.console import Console
from rich.prompt import Confirm

from quaestor.constants import QUAESTOR_DIR_NAME
from quaestor.core.project_metadata import FileManifest
from quaestor.updater import QuaestorUpdater, print_update_result

console = Console()


def update_command(
    path: Path | None = typer.Argument(None, help="Directory to update (default: current directory)"),
    check: bool = typer.Option(False, "--check", "-c", help="Check what would be updated without making changes"),
    backup: bool = typer.Option(True, "--backup/--no-backup", help="Backup files before updating"),
    force: bool = typer.Option(False, "--force", "-f", help="Force update all files (ignore user modifications)"),
):
    """Update Quaestor files to the latest version while preserving user customizations."""
    # Determine target directory
    target_dir = path or Path.cwd()
    quaestor_dir = target_dir / QUAESTOR_DIR_NAME
    manifest_path = quaestor_dir / "manifest.json"

    # Check if .quaestor exists
    if not quaestor_dir.exists():
        console.print(f"[red]No .quaestor directory found in {target_dir}[/red]")
        console.print("[yellow]Run 'quaestor init' first to initialize[/yellow]")
        raise typer.Exit(1)

    # Load manifest
    manifest = FileManifest(manifest_path)

    # Create updater
    updater = QuaestorUpdater(target_dir, manifest)

    if check:
        # Just check what would be updated
        console.print("[blue]Checking for updates...[/blue]")
        updates = updater.check_for_updates(show_diff=True)

        if not updates["needs_update"] and not any(updates["files"].values()):
            console.print("\n[green]✓ Everything is up to date![/green]")
        else:
            console.print("\n[yellow]Updates available. Run 'quaestor update' to apply.[/yellow]")
    else:
        # Perform update
        console.print("[blue]Updating Quaestor files...[/blue]")

        # Show preview first
        updates = updater.check_for_updates(show_diff=True)

        if not updates["needs_update"] and not any(updates["files"].values()):
            console.print("\n[green]✓ Everything is up to date![/green]")
            raise typer.Exit()

        if not force and not Confirm.ask("\n[yellow]Proceed with update?[/yellow]"):
            console.print("[red]Update cancelled.[/red]")
            raise typer.Exit()

        # Do the update
        result = updater.update(backup=backup, force=force)
        print_update_result(result)

        # Save manifest
        manifest.save()

        console.print("\n[green]✅ Update complete![/green]")

        if backup and result.backed_up:
            console.print("[dim]Backup created in .quaestor/.backup/[/dim]")
