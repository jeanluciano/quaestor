"""Configure command for Quaestor."""

from pathlib import Path

import typer
from rich.console import Console
from rich.prompt import Confirm

from quaestor.command_config import CommandConfig

console = Console()


def configure_command(
    path: Path | None = typer.Argument(None, help="Directory to configure (default: current directory)"),
    command: str | None = typer.Option(None, "--command", "-c", help="Command to configure"),
    create_override: bool = typer.Option(False, "--create-override", help="Create a command override file"),
    init_config: bool = typer.Option(False, "--init", help="Initialize command configuration file"),
):
    """Configure project-specific command behavior and overrides."""
    target_dir = path or Path.cwd()
    config = CommandConfig(target_dir)

    # Initialize configuration file
    if init_config:
        if config.config_path.exists():
            console.print("[yellow]Command configuration already exists[/yellow]")
            if not Confirm.ask("Overwrite existing configuration?"):
                raise typer.Exit()

        config.create_default_config()
        console.print(f"[green]✓ Created command configuration at {config.config_path}[/green]")
        console.print("[dim]Edit this file to customize command behavior[/dim]")
        return

    # Create command override
    if create_override and command:
        import importlib.resources as pkg_resources

        # Ensure directories exist
        config.override_dir.mkdir(parents=True, exist_ok=True)
        override_path = config.override_dir / f"{command}.md"

        if override_path.exists():
            console.print(f"[yellow]Override for '{command}' already exists[/yellow]")
            if not Confirm.ask("Overwrite existing override?"):
                raise typer.Exit()

        # Copy example template
        try:
            example_content = pkg_resources.read_text("quaestor.templates", "task-override-example.md")
            # Customize for the specific command
            example_content = example_content.replace("task", command)
            override_path.write_text(example_content)
            console.print(f"[green]✓ Created override template for '{command}' command[/green]")
            console.print(f"[dim]Edit {override_path} to customize the command[/dim]")
        except Exception as e:
            console.print(f"[red]Failed to create override: {e}[/red]")
            raise typer.Exit(1) from e
        return

    # Show current configuration
    if not command:
        console.print("[blue]Current command configuration:[/blue]")

        # Check for config file
        if config.config_path.exists():
            console.print(f"\n[green]✓[/green] Configuration file: {config.config_path}")
            cmd_configs = config.load_config().get("commands", {})
            if cmd_configs:
                console.print("\n[blue]Configured commands:[/blue]")
                for cmd, settings in cmd_configs.items():
                    console.print(f"  • {cmd}: {settings.get('enforcement', 'default')} enforcement")
        else:
            console.print("\n[dim]No configuration file found[/dim]")
            console.print("Run 'quaestor configure --init' to create one")

        # Check for overrides
        overrides = config.get_available_overrides()
        if overrides:
            console.print("\n[blue]Command overrides:[/blue]")
            for override in overrides:
                console.print(f"  • {override}")
        else:
            console.print("\n[dim]No command overrides found[/dim]")
            console.print("Run 'quaestor configure --command <name> --create-override' to create one")
    else:
        # Show specific command configuration
        cmd_config = config.get_command_config(command)
        override_path = config.get_override_path(command)

        console.print(f"\n[blue]Configuration for '{command}' command:[/blue]")

        if cmd_config:
            console.print("\n[green]Settings:[/green]")
            for key, value in cmd_config.items():
                console.print(f"  • {key}: {value}")
        else:
            console.print("\n[dim]No specific configuration[/dim]")

        if override_path:
            console.print(f"\n[green]Override file:[/green] {override_path}")
        else:
            console.print("\n[dim]No override file[/dim]")
