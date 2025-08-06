"""Configuration management CLI commands."""

import json
from pathlib import Path
from typing import Any

import typer
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from quaestor.core.config_manager import ConfigurationError, get_config_manager

console = Console()
config_app = typer.Typer(name="config", help="Configuration management commands")


def _get_nested_value(data: dict, key_path: str) -> Any:
    """Get nested value from dictionary using dot notation.

    Args:
        data: Dictionary to search
        key_path: Dot-separated path (e.g., "languages.python.lint_command")

    Returns:
        Value at the path or None if not found
    """
    keys = key_path.split(".")
    current = data

    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None

    return current


def _set_nested_value(data: dict, key_path: str, value: Any) -> dict:
    """Set nested value in dictionary using dot notation.

    Args:
        data: Dictionary to modify
        key_path: Dot-separated path (e.g., "languages.python.lint_command")
        value: Value to set

    Returns:
        Modified dictionary
    """
    keys = key_path.split(".")
    current = data

    # Navigate to parent of target key
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]

    # Set the final value
    current[keys[-1]] = value
    return data


def _parse_value(value_str: str) -> Any:
    """Parse string value to appropriate Python type.

    Args:
        value_str: String representation of value

    Returns:
        Parsed value with appropriate type
    """
    # Try to parse as JSON first (handles booleans, numbers, lists, dicts)
    try:
        return json.loads(value_str)
    except json.JSONDecodeError:
        pass

    # Handle special string values
    if value_str.lower() in ("true", "false"):
        return value_str.lower() == "true"

    # Try to parse as number
    try:
        if "." in value_str:
            return float(value_str)
        else:
            return int(value_str)
    except ValueError:
        pass

    # Return as string
    return value_str


@config_app.command("show")
def show_config(
    format: str = typer.Option("table", "--format", "-f", help="Output format (table, yaml, json)"),
    project_root: str | None = typer.Option(None, "--project", "-p", help="Project root path"),
    layer_detail: bool = typer.Option(False, "--layers", "-l", help="Show configuration layer details"),
):
    """Show effective configuration with all overrides applied."""
    try:
        project_path = Path(project_root) if project_root else None
        config_manager = get_config_manager(project_path)

        effective_config = config_manager.get_effective_config()

        if format == "json":
            console.print(json.dumps(effective_config, indent=2))
        elif format == "yaml":
            console.print(yaml.dump(effective_config, default_flow_style=False, sort_keys=False))
        elif format == "table":
            _display_config_table(effective_config, layer_detail)
        else:
            console.print(f"[red]Error: Unknown format '{format}'. Use: table, yaml, json[/red]")
            raise typer.Exit(1)

    except ConfigurationError as e:
        console.print(f"[red]Configuration error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


def _display_config_table(config: dict, show_layers: bool = False):
    """Display configuration in table format."""
    # Show project info
    console.print(
        Panel(
            f"[bold]Project Type:[/bold] {config.get('project_type', 'unknown')}\n"
            + f"[bold]Current Language Config:[/bold] {'Available' if config.get('current_language') else 'None'}",
            title="Project Information",
            border_style="blue",
        )
    )

    if show_layers:
        # Show configuration layers
        layer_table = Table(title="Configuration Layers", border_style="green")
        layer_table.add_column("Priority", style="cyan", no_wrap=True)
        layer_table.add_column("Source", style="magenta")
        layer_table.add_column("Description", style="white")
        layer_table.add_column("Exists", style="green")

        for layer in config.get("layers", []):
            exists = "✓" if layer.get("exists", False) else "✗"
            layer_table.add_row(str(layer["priority"]), layer["source"], layer["description"], exists)

        console.print(layer_table)
        console.print()

    # Show current language configuration if available
    current_lang_config = config.get("current_language")
    if current_lang_config:
        lang_table = Table(
            title=f"Current Language Configuration ({config.get('project_type', 'unknown')})", border_style="yellow"
        )
        lang_table.add_column("Setting", style="cyan", no_wrap=True)
        lang_table.add_column("Value", style="white")

        for key, value in current_lang_config.items():
            if value is not None:
                lang_table.add_row(key, str(value))

        console.print(lang_table)
        console.print()

    # Show main configuration
    main_config = config.get("main", {})
    if main_config:
        main_table = Table(title="Main Configuration", border_style="blue")
        main_table.add_column("Section", style="cyan", no_wrap=True)
        main_table.add_column("Settings", style="white")

        for section, settings in main_config.items():
            if isinstance(settings, dict):
                settings_str = "\n".join([f"{k}: {v}" for k, v in settings.items()])
            else:
                settings_str = str(settings)
            main_table.add_row(section, settings_str)

        console.print(main_table)


@config_app.command("get")
def get_config_value(
    key: str = typer.Argument(..., help="Configuration key (dot notation, e.g., 'languages.python.lint_command')"),
    project_root: str | None = typer.Option(None, "--project", "-p", help="Project root path"),
    format: str = typer.Option("value", "--format", "-f", help="Output format (value, json, yaml)"),
):
    """Get a specific configuration value."""
    try:
        project_path = Path(project_root) if project_root else None
        config_manager = get_config_manager(project_path)

        effective_config = config_manager.get_effective_config()
        value = _get_nested_value(effective_config, key)

        if value is None:
            console.print(f"[yellow]Configuration key '{key}' not found[/yellow]")
            raise typer.Exit(1)

        if format == "json":
            console.print(json.dumps(value, indent=2))
        elif format == "yaml":
            console.print(yaml.dump(value, default_flow_style=False))
        elif format == "value":
            if isinstance(value, dict | list):
                console.print(json.dumps(value, indent=2))
            else:
                console.print(str(value))
        else:
            console.print(f"[red]Error: Unknown format '{format}'. Use: value, json, yaml[/red]")
            raise typer.Exit(1)

    except ConfigurationError as e:
        console.print(f"[red]Configuration error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@config_app.command("set")
def set_config_value(
    key: str = typer.Argument(..., help="Configuration key (dot notation)"),
    value: str = typer.Argument(..., help="Value to set (auto-parsed from string)"),
    project_root: str | None = typer.Option(None, "--project", "-p", help="Project root path"),
    config_type: str = typer.Option("main", "--type", "-t", help="Config type (main, languages, commands)"),
    force: bool = typer.Option(False, "--force", help="Force creation of new configuration sections"),
):
    """Set a configuration override value."""
    try:
        project_path = Path(project_root) if project_root else None
        config_manager = get_config_manager(project_path)

        # Parse the value
        parsed_value = _parse_value(value)

        # Create update dictionary
        config_updates = {}
        _set_nested_value(config_updates, key, parsed_value)

        # Determine config type based on key if not specified
        if key.startswith("languages.") and config_type == "main":
            config_type = "languages"
        elif key.startswith("commands.") and config_type == "main":
            config_type = "commands"

        # Save the configuration
        success = config_manager.save_project_config(config_updates, config_type)

        if success:
            console.print(
                f"[green]✓[/green] Configuration updated: [cyan]{key}[/cyan] = [yellow]{parsed_value}[/yellow]"
            )
            console.print(f"[dim]Saved to: {config_type} configuration[/dim]")
        else:
            console.print("[red]Failed to save configuration[/red]")
            raise typer.Exit(1)

    except ConfigurationError as e:
        console.print(f"[red]Configuration error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@config_app.command("reset")
def reset_config(
    config_type: str = typer.Option(
        "all", "--type", "-t", help="Config type to reset (all, main, languages, commands)"
    ),
    project_root: str | None = typer.Option(None, "--project", "-p", help="Project root path"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
):
    """Reset configuration to defaults."""
    try:
        project_path = Path(project_root) if project_root else None
        config_manager = get_config_manager(project_path)

        # Confirmation prompt
        if not confirm:
            if config_type == "all":
                message = "Are you sure you want to reset ALL project configurations to defaults?"
            else:
                message = f"Are you sure you want to reset {config_type} configuration to defaults?"

            if not typer.confirm(message):
                console.print("Reset cancelled.")
                raise typer.Exit(0)

        quaestor_dir = config_manager.quaestor_dir

        files_to_remove = []
        if config_type in ("all", "main"):
            config_file = quaestor_dir / "config.yaml"
            if config_file.exists():
                files_to_remove.append(("Main configuration", config_file))

        if config_type in ("all", "languages"):
            lang_file = quaestor_dir / "languages.yaml"
            if lang_file.exists():
                files_to_remove.append(("Language overrides", lang_file))

        if config_type in ("all", "commands"):
            cmd_file = quaestor_dir / "command-config.yaml"
            if cmd_file.exists():
                files_to_remove.append(("Command configuration", cmd_file))

        if not files_to_remove:
            console.print(f"[yellow]No {config_type} configuration files found to reset[/yellow]")
            raise typer.Exit(0)

        # Remove the files
        removed_count = 0
        for desc, file_path in files_to_remove:
            try:
                file_path.unlink()
                console.print(f"[green]✓[/green] Reset {desc}: [dim]{file_path}[/dim]")
                removed_count += 1
            except Exception as e:
                console.print(f"[red]Failed to reset {desc}: {e}[/red]")

        if removed_count > 0:
            # Reinitialize defaults if needed
            config_manager.initialize_default_configs()
            console.print(f"[green]Successfully reset {removed_count} configuration file(s)[/green]")

    except ConfigurationError as e:
        console.print(f"[red]Configuration error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@config_app.command("validate")
def validate_config(
    project_root: str | None = typer.Option(None, "--project", "-p", help="Project root path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed validation results"),
):
    """Validate current configuration and show any issues."""
    try:
        project_path = Path(project_root) if project_root else None
        config_manager = get_config_manager(project_path)

        validation_result = config_manager.validate_configuration()

        if validation_result.valid:
            console.print("[green]✓ Configuration is valid[/green]")
        else:
            console.print("[red]✗ Configuration has errors[/red]")

        if validation_result.warnings:
            console.print("\n[yellow]Warnings:[/yellow]")
            for warning in validation_result.warnings:
                console.print(f"  [yellow]•[/yellow] {warning}")

        if validation_result.errors:
            console.print("\n[red]Errors:[/red]")
            for error in validation_result.errors:
                console.print(f"  [red]•[/red] {error}")

        if verbose or validation_result.errors:
            console.print("\n[dim]Run 'quaestor config show --layers' to see configuration layer details[/dim]")

        if not validation_result.valid:
            raise typer.Exit(1)

    except ConfigurationError as e:
        console.print(f"[red]Configuration error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@config_app.command("init")
def init_config(
    project_root: str | None = typer.Option(None, "--project", "-p", help="Project root path"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing configuration files"),
):
    """Initialize default configuration files."""
    try:
        project_path = Path(project_root) if project_root else None
        config_manager = get_config_manager(project_path)

        quaestor_dir = config_manager.quaestor_dir

        # Check if files already exist
        existing_files = []
        config_file = quaestor_dir / "config.yaml"
        cmd_config_file = quaestor_dir / "command-config.yaml"

        if config_file.exists():
            existing_files.append("config.yaml")
        if cmd_config_file.exists():
            existing_files.append("command-config.yaml")

        if existing_files and not force:
            console.print(f"[yellow]Configuration files already exist: {', '.join(existing_files)}[/yellow]")
            console.print("Use --force to overwrite existing files")
            raise typer.Exit(1)

        # Initialize configuration files
        success = config_manager.initialize_default_configs()

        if success:
            console.print(f"[green]✓ Configuration initialized in:[/green] [dim]{quaestor_dir}[/dim]")
            console.print("\nFiles created:")
            if config_file.exists():
                console.print("  [cyan]•[/cyan] config.yaml - Main configuration")
            if cmd_config_file.exists():
                console.print("  [cyan]•[/cyan] command-config.yaml - Command configuration")
        else:
            console.print("[red]Failed to initialize configuration[/red]")
            raise typer.Exit(1)

    except ConfigurationError as e:
        console.print(f"[red]Configuration error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    config_app()
