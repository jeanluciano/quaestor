"""Initialization commands for Quaestor."""

import importlib.resources as pkg_resources
import tempfile
from pathlib import Path

import typer
from rich.console import Console

from quaestor.constants import (
    COMMAND_FILES,
    DEFAULT_COMMANDS_DIR,
    QUAESTOR_CONFIG_END,
    QUAESTOR_CONFIG_START,
    QUAESTOR_DIR_NAME,
    TEMPLATE_BASE_PATH,
    TEMPLATE_FILES,
)
from quaestor.core import update_gitignore
from quaestor.core.project_metadata import FileManifest, FileType, extract_version_from_content
from quaestor.core.template_engine import get_project_data, process_template
from quaestor.core.updater import QuaestorUpdater, print_update_result

console = Console()


def init_command(
    path: Path | None = typer.Argument(None, help="Directory to initialize (default: current directory)"),
    mode: str = typer.Option("personal", "--mode", "-m", help="Mode: 'personal' (default) or 'team'"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing .quaestor directory"),
    contextual: bool = typer.Option(
        True, "--contextual/--no-contextual", help="Generate contextual rules based on project analysis"
    ),
):
    """Initialize Quaestor with personal or team mode.

    Personal mode (default): All files stored locally in project.
    Team mode: Commands installed globally, project files in .quaestor.
    """
    # Validate mode
    if mode not in ["personal", "team"]:
        console.print(f"[red]Invalid mode: {mode}. Use 'personal' or 'team'.[/red]")
        raise typer.Exit(1)

    # Determine target directory
    target_dir = path or Path.cwd()

    # Route to appropriate initialization function
    if mode == "personal":
        _init_personal_mode(target_dir, force)
    else:
        _init_team_mode(target_dir, force, contextual)


def _init_personal_mode(target_dir: Path, force: bool):
    """Initialize in personal mode (all files local to project)."""
    # Set up directories
    claude_dir = target_dir / ".claude"
    quaestor_dir = target_dir / QUAESTOR_DIR_NAME
    hooks_dir = quaestor_dir / "hooks"
    manifest_path = quaestor_dir / "manifest.json"

    # Load or create manifest
    manifest = FileManifest(manifest_path)

    # Check if this is an update scenario
    if quaestor_dir.exists() and not force:
        # Use updater for existing installations
        updater = QuaestorUpdater(target_dir, manifest)

        # Check what would be updated
        console.print("[blue]Checking for updates...[/blue]")
        updates = updater.check_for_updates(show_diff=True)

        if not updates["needs_update"] and not any(updates["files"].values()):
            console.print("\n[green]✓ Everything is up to date![/green]")
            raise typer.Exit()

        from rich.prompt import Confirm

        if not Confirm.ask("\n[yellow]Proceed with update?[/yellow]"):
            console.print("[red]Update cancelled.[/red]")
            raise typer.Exit()

        # Perform update
        result = updater.update(backup=True)
        print_update_result(result)

        # Save manifest
        manifest.save()
        console.print("\n[green]✅ Update complete![/green]")
        raise typer.Exit()

    # Fresh installation
    if claude_dir.exists() and force:
        console.print("[yellow]Force flag set - overwriting existing personal installation[/yellow]")

    # Create directories
    claude_dir.mkdir(exist_ok=True)
    quaestor_dir.mkdir(exist_ok=True)
    hooks_dir.mkdir(exist_ok=True)
    (claude_dir / "commands").mkdir(exist_ok=True)
    console.print(f"[green]Created .claude directory (personal mode) in {target_dir}[/green]")

    # Set quaestor version in manifest
    from .. import __version__

    manifest.set_quaestor_version(__version__)

    # Handle CLAUDE.md - same as team mode (in project root)
    _merge_claude_md(target_dir, use_rule_engine=False)

    # Create settings.local.json for hooks configuration using uvx
    settings_path = claude_dir / "settings.local.json"
    try:
        settings_content = pkg_resources.read_text("quaestor.claude.hooks", "settings_uvx.json")
        settings_path.write_text(settings_content)
        console.print("  [blue]✓[/blue] Created settings.local.json for hooks (uses uvx commands)")
    except Exception as e:
        console.print(f"  [yellow]⚠[/yellow] Could not create settings.local.json: {e}")

    # Copy hook files to .quaestor/hooks for personal mode
    console.print("\n[blue]Installing hook files:[/blue]")
    hook_files = ["base.py", "session_context_loader.py", "todo_spec_progress.py"]
    hooks_copied = 0
    for hook_file in hook_files:
        try:
            hook_content = pkg_resources.read_text("quaestor.claude.hooks", hook_file)
            (hooks_dir / hook_file).write_text(hook_content)
            console.print(f"  [blue]✓[/blue] Installed {hook_file}")
            hooks_copied += 1
        except Exception as e:
            console.print(f"  [yellow]⚠[/yellow] Could not install {hook_file}: {e}")
    console.print(f"  [green]Installed {hooks_copied} hook files[/green]")

    # Copy system files to .quaestor directory (for manifest tracking)
    _copy_system_files(quaestor_dir, manifest, target_dir)

    # Common initialization
    copied_files, commands_copied = _init_common(target_dir, force, "personal")

    # Track template files in manifest
    for _template_name, output_name in TEMPLATE_FILES.items():
        output_path = quaestor_dir / output_name
        if output_path.exists():
            content = output_path.read_text()
            version = extract_version_from_content(content) or "1.0"
            manifest.track_file(output_path, FileType.USER_EDITABLE, version, target_dir)

    # Save manifest
    manifest.save()

    # Summary
    if copied_files or commands_copied > 0:
        console.print("\n[green]✅ Personal mode initialization complete![/green]")

        if copied_files:
            console.print(f"\n[blue]Project files ({len(copied_files)}):[/blue]")
            for file in copied_files:
                console.print(f"  • {file}")

        console.print("\n[blue]Next steps:[/blue]")
        console.print("  • Personal commands are available globally")
        console.print("  • Claude will automatically discover CLAUDE.md")
        console.print("  • Use 'quaestor init' to check for updates")
    else:
        console.print("[red]No files were copied. Please check the source files exist.[/red]")
        raise typer.Exit(1)


def _init_team_mode(target_dir: Path, force: bool, contextual: bool = True):
    """Initialize in team mode (original behavior)."""
    quaestor_dir = target_dir / QUAESTOR_DIR_NAME
    manifest_path = quaestor_dir / "manifest.json"

    # Load or create manifest
    manifest = FileManifest(manifest_path)

    # Check if this is an update scenario
    if quaestor_dir.exists() and not force:
        # Use updater for existing installations
        updater = QuaestorUpdater(target_dir, manifest)

        # Check what would be updated
        console.print("[blue]Checking for updates...[/blue]")
        updates = updater.check_for_updates(show_diff=True)

        if not updates["needs_update"] and not any(updates["files"].values()):
            console.print("\n[green]✓ Everything is up to date![/green]")
            raise typer.Exit()

        from rich.prompt import Confirm

        if not Confirm.ask("\n[yellow]Proceed with update?[/yellow]"):
            console.print("[red]Update cancelled.[/red]")
            raise typer.Exit()

        # Perform update
        result = updater.update(backup=True)
        print_update_result(result)

        # Save manifest
        manifest.save()
        console.print("\n[green]✅ Update complete![/green]")
        raise typer.Exit()

    # Fresh installation
    if quaestor_dir.exists() and force:
        console.print("[yellow]Force flag set - overwriting existing installation[/yellow]")

    # Create directories
    quaestor_dir.mkdir(exist_ok=True)
    console.print(f"[green]Created .quaestor directory in {target_dir}[/green]")

    # Set quaestor version in manifest
    from .. import __version__

    manifest.set_quaestor_version(__version__)

    # Handle CLAUDE.md - always use simple format for team mode
    _merge_claude_md(target_dir, use_rule_engine=False)

    # Create .claude/settings.json for team mode
    claude_dir = target_dir / ".claude"
    claude_dir.mkdir(exist_ok=True)
    settings_path = claude_dir / "settings.json"
    try:
        settings_content = pkg_resources.read_text("quaestor.claude.hooks", "settings_uvx.json")
        settings_path.write_text(settings_content)
        console.print("  [blue]✓[/blue] Created settings.json for hooks (uses uvx commands)")
    except Exception as e:
        console.print(f"  [yellow]⚠[/yellow] Could not create settings.json: {e}")

    # Copy system files
    _copy_system_files(quaestor_dir, manifest, target_dir)

    # Common initialization
    copied_files, commands_copied = _init_common(target_dir, force, "team")

    # Track template files in manifest
    for _template_name, output_name in TEMPLATE_FILES.items():
        output_path = quaestor_dir / output_name
        if output_path.exists():
            content = output_path.read_text()
            version = extract_version_from_content(content) or "1.0"
            manifest.track_file(output_path, FileType.USER_EDITABLE, version, target_dir)

    # Save manifest
    manifest.save()

    # Summary
    console.print("\n[green]✅ Team mode initialization complete![/green]")
    console.print(f"\n[blue]Project files ({len(copied_files)}):[/blue]")
    for file in copied_files:
        console.print(f"  • {file}")


def _merge_claude_md(target_dir: Path, use_rule_engine: bool = False) -> bool:
    """Merge Quaestor include section with existing CLAUDE.md or create new one."""
    claude_path = target_dir / "CLAUDE.md"

    try:
        # Get the include template
        try:
            include_content = pkg_resources.read_text("quaestor.claude", "include.md")
        except Exception:
            # Fallback if template is missing
            include_content = """<!-- QUAESTOR CONFIG START -->
[!IMPORTANT]
**Claude:** This project uses Quaestor for AI context management.
Please read the following files in order:
@.quaestor/AGENT.md - Complete AI development context and rules
@.quaestor/ARCHITECTURE.md - System design and structure (if available)
@.quaestor/RULES.md
@.quaestor/specs/active/ - Active specifications and implementation details
<!-- QUAESTOR CONFIG END -->

<!-- Your custom content below -->
"""

        if claude_path.exists():
            # Read existing content
            existing_content = claude_path.read_text()

            # Check if already has Quaestor config
            if QUAESTOR_CONFIG_START in existing_content:
                # Update existing config section
                start_idx = existing_content.find(QUAESTOR_CONFIG_START)
                end_idx = existing_content.find(QUAESTOR_CONFIG_END)

                if end_idx == -1:
                    console.print("[yellow]⚠ CLAUDE.md has invalid Quaestor markers. Creating backup...[/yellow]")
                    claude_path.rename(target_dir / "CLAUDE.md.backup")
                    claude_path.write_text(include_content)
                else:
                    # Extract config section from template
                    config_start = include_content.find(QUAESTOR_CONFIG_START)
                    config_end = include_content.find(QUAESTOR_CONFIG_END) + len(QUAESTOR_CONFIG_END)
                    new_config = include_content[config_start:config_end]

                    # Replace old config with new
                    new_content = (
                        existing_content[:start_idx]
                        + new_config
                        + existing_content[end_idx + len(QUAESTOR_CONFIG_END) :]
                    )
                    claude_path.write_text(new_content)
                    console.print("  [blue]↻[/blue] Updated Quaestor config in existing CLAUDE.md")
            else:
                # Prepend Quaestor config to existing content
                template_lines = include_content.strip().split("\n")
                if template_lines[-1] == "<!-- Your custom content below -->":
                    template_lines = template_lines[:-1]

                merged_content = "\n".join(template_lines) + "\n\n" + existing_content
                claude_path.write_text(merged_content)
                console.print("  [blue]✓[/blue] Added Quaestor config to existing CLAUDE.md")
        else:
            # Create new file
            claude_path.write_text(include_content)
            console.print("  [blue]✓[/blue] Created CLAUDE.md with Quaestor config")

        return True

    except Exception as e:
        console.print(f"  [red]✗[/red] Failed to handle CLAUDE.md: {e}")
        return False


def _copy_system_files(quaestor_dir: Path, manifest: FileManifest, target_dir: Path):
    """Copy system files to .quaestor directory."""
    # Copy AGENT.md (consolidated template)
    try:
        context_content = pkg_resources.read_text("quaestor.claude", "agent.md")
        context_path = quaestor_dir / "AGENT.md"
        context_path.write_text(context_content)

        # Track in manifest
        version = extract_version_from_content(context_content) or "1.0"
        manifest.track_file(context_path, FileType.SYSTEM, version, target_dir)
        console.print("  [blue]✓[/blue] Copied AGENT.md")
    except Exception as e:
        console.print(f"  [yellow]⚠[/yellow] Could not copy AGENT.md: {e}")


def _init_common(target_dir: Path, force: bool, mode: str):
    """Common initialization logic for both modes."""

    # Process and copy template files to .quaestor
    quaestor_dir = target_dir / QUAESTOR_DIR_NAME
    quaestor_dir.mkdir(exist_ok=True)

    console.print("\n[blue]Setting up documentation files:[/blue]")

    # Get project data for templates
    project_data = get_project_data(target_dir)

    # Process each template file
    copied_files = []
    for template_name, output_name in TEMPLATE_FILES.items():
        try:
            output_path = quaestor_dir / output_name

            # Process template with project data
            try:
                template_content = pkg_resources.read_text(TEMPLATE_BASE_PATH, template_name)
                # Create a temporary file to process
                with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as tf:
                    tf.write(template_content)
                    temp_path = Path(tf.name)

                ai_content = process_template(temp_path, project_data)
                temp_path.unlink()  # Clean up temp file
            except Exception:
                ai_content = None

            if ai_content:
                output_path.write_text(ai_content)
                copied_files.append(f".quaestor/{output_name}")
                console.print(f"  [blue]✓[/blue] Created {output_name}")
        except Exception as e:
            console.print(f"  [yellow]⚠[/yellow] Could not create {output_name}: {e}")

    # Copy commands
    console.print("\n[blue]Installing command files:[/blue]")

    if mode == "personal":
        commands_dir = DEFAULT_COMMANDS_DIR  # Personal mode: install to ~/.claude/commands
        commands_dir.mkdir(parents=True, exist_ok=True)
        console.print("Installing to ~/.claude/commands (personal commands)")
    else:
        commands_dir = target_dir / ".claude" / "commands"  # Team mode: install to .claude/commands
        commands_dir.mkdir(parents=True, exist_ok=True)
        console.print("Installing to .claude/commands (project commands)")

    # Get the source commands directory
    # In a uv workspace or development mode, the source is relative to this file
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent.parent  # Go up from src/quaestor/cli/init.py
    source_commands_dir = project_root / ".claude" / "commands"

    # Fallback: try to find from package location
    if not source_commands_dir.exists():
        import quaestor

        package_dir = Path(quaestor.__file__).parent.parent
        source_commands_dir = package_dir / ".claude" / "commands"

    # Copy command files directly without configuration processing
    commands_copied = 0

    if source_commands_dir.exists():
        # Copy all command files from .claude/commands
        for cmd_file in source_commands_dir.glob("*.md"):
            try:
                cmd_content = cmd_file.read_text()
                (commands_dir / cmd_file.name).write_text(cmd_content)
                console.print(f"  [blue]✓[/blue] Installed {cmd_file.name}")
                commands_copied += 1
            except Exception as e:
                console.print(f"  [yellow]⚠[/yellow] Could not install {cmd_file.name}: {e}")
    else:
        # Fallback to using package resources if directory not found
        for cmd_file in COMMAND_FILES:
            try:
                # Read command content directly from package
                cmd_content = pkg_resources.read_text("quaestor.claude.commands", cmd_file)
                (commands_dir / cmd_file).write_text(cmd_content)
                console.print(f"  [blue]✓[/blue] Installed {cmd_file} (from package)")
                commands_copied += 1
            except Exception as e:
                console.print(f"  [yellow]⚠[/yellow] Could not install {cmd_file}: {e}")

    # Copy hook files
    # No longer need to copy hook files - hooks are called via uvx commands
    console.print("\n[blue]Hooks configured to use uvx commands (no files to copy)[/blue]")

    # Copy agent files for team mode
    if mode == "team":
        console.print("\n[blue]Installing agent files:[/blue]")

        agents_dir = target_dir / ".claude" / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)

        # Get the source agents directory
        # In a uv workspace or development mode, the source is relative to this file
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent.parent  # Go up from src/quaestor/cli/init.py
        source_agents_dir = project_root / ".claude" / "agents"

        # Fallback: try to find from package location
        if not source_agents_dir.exists():
            import quaestor

            package_dir = Path(quaestor.__file__).parent.parent
            source_agents_dir = package_dir / ".claude" / "agents"

        agents_copied = 0
        if source_agents_dir.exists():
            # Copy all agent files from .claude/agents
            for agent_file in source_agents_dir.glob("*.md"):
                try:
                    agent_content = agent_file.read_text()
                    (agents_dir / agent_file.name).write_text(agent_content)
                    console.print(f"  [blue]✓[/blue] Installed {agent_file.name}")
                    agents_copied += 1
                except Exception as e:
                    console.print(f"  [yellow]⚠[/yellow] Could not install {agent_file.name}: {e}")
        else:
            console.print(f"  [red]✗[/red] Source agents directory not found at {source_agents_dir}")

        console.print(f"\n  [green]Installed {agents_copied} agent files[/green]")

    # Update gitignore
    if mode == "personal":
        entries = [
            "# Quaestor Personal Mode",
            ".quaestor/",  # Only ignore .quaestor directory in personal mode
            ".claude/settings.local.json",  # Ignore local settings
        ]
        update_gitignore(target_dir, entries, "Quaestor")
    # Team mode: don't modify gitignore at all

    return copied_files, commands_copied
