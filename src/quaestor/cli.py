import importlib.resources as pkg_resources
from pathlib import Path

import typer
from rich.console import Console
from rich.prompt import Confirm

from . import __version__
from .command_config import CommandConfig
from .constants import (
    COMMAND_FILES,
    DEFAULT_COMMANDS_DIR,
    QUAESTOR_CONFIG_END,
    QUAESTOR_CONFIG_START,
    QUAESTOR_DIR_NAME,
)
from .converters import convert_manifest_to_ai_format
from .manifest import FileManifest, FileType, extract_version_from_content
from .rule_engine import RuleEngine
from .updater import QuaestorUpdater, print_update_result

app = typer.Typer(
    name="quaestor",
    help="Quaestor - Context management for AI-assisted development",
    add_completion=False,
)
console = Console()


@app.callback()
def callback():
    """Quaestor - Context management for AI-assisted development."""
    pass


def _update_gitignore(target_dir: Path, mode: str):
    """Update .gitignore with appropriate entries for the given mode."""
    gitignore_path = target_dir / ".gitignore"

    # Define entries for each mode
    personal_entries = [
        "# Quaestor Personal Mode",
        ".claude/",
        ".quaestor/cache/",
        ".quaestor/user/",
        ".quaestor/local/",
    ]

    team_entries = [
        "# Quaestor Team Mode",
        ".claude/settings.json",  # Only ignore hooks in team mode
        ".quaestor/cache/",
        ".quaestor/user/",
        ".quaestor/local/",
        ".quaestor/personal/",
    ]

    entries_to_add = personal_entries if mode == "personal" else team_entries

    try:
        # Read existing .gitignore
        existing_content = ""
        if gitignore_path.exists():
            existing_content = gitignore_path.read_text()

        # Check if Quaestor section already exists
        if "# Quaestor" in existing_content:
            console.print("  [dim]○[/dim] .gitignore already has Quaestor entries")
            return

        # Add new entries
        if existing_content and not existing_content.endswith("\n"):
            existing_content += "\n"

        new_content = existing_content + "\n" + "\n".join(entries_to_add) + "\n"
        gitignore_path.write_text(new_content)

        console.print(f"  [blue]✓[/blue] Updated .gitignore for {mode} mode")
    except Exception as e:
        console.print(f"  [yellow]⚠[/yellow] Could not update .gitignore: {e}")


def merge_claude_md(target_dir: Path, use_rule_engine: bool = False) -> bool:
    """Merge Quaestor include section with existing CLAUDE.md or create new one.

    Args:
        target_dir: Project root directory
        use_rule_engine: Whether to use RuleEngine for generation

    Returns:
        True if successful, False otherwise
    """
    claude_path = target_dir / "CLAUDE.md"

    try:
        if use_rule_engine:
            # Generate using RuleEngine for team mode
            console.print("  [blue]→[/blue] Analyzing project for team mode rules...")
            rule_engine = RuleEngine(target_dir)
            claude_content = rule_engine.generate_claude_md(mode="team")
            claude_path.write_text(claude_content)
            console.print("  [blue]✓[/blue] Created context-aware CLAUDE.md for team mode")
            return True
        # Get the include template
        try:
            include_content = pkg_resources.read_text("quaestor.templates", "CLAUDE_INCLUDE.md")
        except Exception:
            # Fallback if template is missing - create minimal include content
            include_content = """<!-- QUAESTOR CONFIG START -->
> [!IMPORTANT]
> **Claude:** This project uses Quaestor for AI context management.
> Please read the following files in order:
> 1. `.quaestor/QUAESTOR_CLAUDE.md` - How to work with this project effectively
> 2. `.quaestor/CRITICAL_RULES.md` - Critical rules you must follow
> 3. `.quaestor/ARCHITECTURE.md` - System design and structure (if available)
> 4. `.quaestor/MEMORY.md` - Implementation patterns and decisions (if available)
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
                # Remove the "Your custom content below" line from template
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


def copy_hook_scripts(target_dir: Path) -> bool:
    """Copy hook scripts to .quaestor/hooks directory."""
    try:
        hooks_dir = target_dir / ".quaestor" / "hooks"
        hooks_dir.mkdir(parents=True, exist_ok=True)

        # List of hook scripts to copy
        hook_scripts = [
            "enforce-research.py",
            "track-research.py",
            "track-implementation.py",
            "update-memory.py",
            "quality-check.py",
            "check-milestone.py",
            "refresh-context.py",
            "pre-implementation-declaration.py",
            "todo-milestone-connector.py",
            "file-change-tracker.py",
            "milestone-validator.py",
            "comprehensive-compliance-check.py",
            "auto-commit-trigger.py",
        ]

        for script in hook_scripts:
            try:
                content = pkg_resources.read_text("quaestor.templates.hooks", script)
                script_path = hooks_dir / script
                script_path.write_text(content)
                # Make executable
                script_path.chmod(0o755)
            except Exception as e:
                console.print(f"  [yellow]⚠[/yellow] Could not copy {script}: {e}")

        return True
    except Exception as e:
        console.print(f"  [red]✗[/red] Failed to copy hook scripts: {e}")
        return False


def generate_hooks_json(target_dir: Path, project_type: str) -> Path | None:
    """Generate hooks.json from template and install to .claude/settings."""
    try:
        # First copy the hook scripts
        copy_hook_scripts(target_dir)

        # Try to use Jinja2 if available
        try:
            from jinja2 import Template

            template_content = pkg_resources.read_text("quaestor.templates", "hooks.json.jinja2")
            # Remove Jinja2 comment line if present
            template_lines = template_content.split("\n")
            if template_lines[0].strip().startswith("{#") and template_lines[0].strip().endswith("#}"):
                template_content = "\n".join(template_lines[1:])

            template = Template(template_content)

            # Render template with context
            hooks_content = template.render(
                project_type=project_type,
                python_path="python3",
                project_root=str(target_dir),
            )
        except ImportError:
            # Fallback to basic template without Jinja2
            template_content = pkg_resources.read_text("quaestor.templates", "hooks_base.json")

            # Determine quality tools based on project type
            if project_type == "python":
                linter = "ruff"
                formatter = "ruff format"
                test_runner = "pytest"
            elif project_type == "rust":
                linter = "cargo clippy"
                formatter = "rustfmt"
                test_runner = "cargo test"
            elif project_type == "javascript":
                linter = "eslint"
                formatter = "prettier"
                test_runner = "npm test"
            else:
                linter = "none"
                formatter = "none"
                test_runner = "none"

            # Basic string replacements
            hooks_content = template_content.replace("{project_type}", project_type)
            hooks_content = hooks_content.replace("{python_path}", "python3")
            hooks_content = hooks_content.replace("{project_root}", str(target_dir))
            hooks_content = hooks_content.replace("{linter}", linter)
            hooks_content = hooks_content.replace("{formatter}", formatter)
            hooks_content = hooks_content.replace("{test_runner}", test_runner)

        # Create .claude directory in project root
        claude_dir = target_dir / ".claude"
        claude_dir.mkdir(parents=True, exist_ok=True)

        # Write hooks to .claude/settings.json
        hooks_path = claude_dir / "settings.json"
        hooks_path.write_text(hooks_content)

        return hooks_path

    except Exception as e:
        console.print(f"[yellow]Failed to generate hooks.json: {e}[/yellow]")
        return None


@app.command(name="init")
def init(
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
    # Set up .claude directory in project root
    claude_dir = target_dir / ".claude"
    claude_commands_dir = claude_dir / "commands"
    claude_context_dir = claude_dir / "context"

    # Optional .quaestor for architecture/memory
    quaestor_dir = target_dir / QUAESTOR_DIR_NAME

    # Check if this is a fresh install or update
    if claude_dir.exists() and not force:
        console.print(f"[yellow].claude directory already exists in {target_dir}[/yellow]")
        console.print("[yellow]Use --force to overwrite existing installation[/yellow]")
        raise typer.Exit(1)

    # Fresh installation
    if claude_dir.exists() and force:
        console.print("[yellow]Force flag set - overwriting existing personal installation[/yellow]")

    # Create directories
    claude_dir.mkdir(exist_ok=True)
    claude_commands_dir.mkdir(exist_ok=True)
    claude_context_dir.mkdir(exist_ok=True)
    console.print(f"[green]Created .claude directory (personal mode) in {target_dir}[/green]")

    # Optionally create .quaestor for architecture/memory
    quaestor_dir.mkdir(exist_ok=True)
    console.print("[green]Created .quaestor directory for architecture and memory tracking[/green]")

    # Copy files using package resources
    copied_files = []

    # Create CLAUDE.md in .claude directory for personal mode
    claude_path = claude_dir / "CLAUDE.md"
    try:
        # Use RuleEngine to generate contextual CLAUDE.md
        console.print("  [blue]→[/blue] Analyzing project complexity...")
        rule_engine = RuleEngine(target_dir)
        claude_content = rule_engine.generate_claude_md(mode="personal")

        claude_path.write_text(claude_content)
        copied_files.append(".claude/CLAUDE.md")
        console.print("  [blue]✓[/blue] Created context-aware CLAUDE.md in .claude directory")
    except Exception as e:
        console.print(f"  [yellow]⚠[/yellow] Could not create CLAUDE.md: {e}")

    # Copy commands to .claude/commands (local to project)
    console.print("\n[blue]Installing command files to .claude/commands:[/blue]")
    command_files = COMMAND_FILES
    commands_copied = 0

    for cmd_file in command_files:
        try:
            cmd_content = pkg_resources.read_text("quaestor.commands", cmd_file)
            (claude_commands_dir / cmd_file).write_text(cmd_content)
            console.print(f"  [blue]✓[/blue] Installed {cmd_file}")
            commands_copied += 1
        except Exception as e:
            console.print(f"  [yellow]⚠[/yellow] Could not install {cmd_file}: {e}")

    # Copy ARCHITECTURE.md and MEMORY.md to .quaestor
    console.print("\n[blue]Setting up architecture and memory files:[/blue]")

    # ARCHITECTURE.md
    try:
        arch_path = quaestor_dir / "ARCHITECTURE.md"
        try:
            arch_content = pkg_resources.read_text("quaestor.manifest", "ARCHITECTURE.md")
            ai_arch_content = convert_manifest_to_ai_format(arch_content, "ARCHITECTURE.md")
        except Exception:
            try:
                ai_arch_content = pkg_resources.read_text("quaestor.templates", "ARCHITECTURE.template.md")
            except Exception:
                ai_arch_content = None

        if ai_arch_content:
            arch_path.write_text(ai_arch_content)
            copied_files.append(".quaestor/ARCHITECTURE.md")
            console.print("  [blue]✓[/blue] Created ARCHITECTURE.md")
    except Exception:
        pass

    # MEMORY.md
    try:
        mem_path = quaestor_dir / "MEMORY.md"
        try:
            mem_content = pkg_resources.read_text("quaestor.manifest", "MEMORY.md")
            ai_mem_content = convert_manifest_to_ai_format(mem_content, "MEMORY.md")
        except Exception:
            try:
                ai_mem_content = pkg_resources.read_text("quaestor.templates", "MEMORY.template.md")
            except Exception:
                ai_mem_content = None

        if ai_mem_content:
            mem_path.write_text(ai_mem_content)
            copied_files.append(".quaestor/MEMORY.md")
            console.print("  [blue]✓[/blue] Created MEMORY.md")
    except Exception:
        pass

    # Generate and install hooks
    console.print("\n[blue]Installing Claude hooks configuration:[/blue]")
    try:
        from .hooks import detect_project_type

        project_type = detect_project_type(target_dir)
        # For personal mode, hooks go in .claude/settings.json
        hooks_json_path = generate_hooks_json(target_dir, project_type)
        if hooks_json_path:
            console.print("  [blue]✓[/blue] Installed hooks in .claude/settings.json")
            console.print("    [green]Hooks are now active for this project![/green]")
            copied_files.append(".claude/settings.json")
    except Exception as e:
        console.print(f"  [yellow]⚠[/yellow] Could not install hooks: {e}")

    # Generate .gitignore entries
    _update_gitignore(target_dir, mode="personal")

    # Summary
    if copied_files or commands_copied > 0:
        console.print("\n[green]✅ Personal mode initialization complete![/green]")

        if copied_files:
            console.print(f"\n[blue]Project files ({len(copied_files)}):[/blue]")
            for file in copied_files:
                console.print(f"  • {file}")

        if commands_copied > 0:
            console.print(f"\n[blue]Commands installed locally ({commands_copied}):[/blue]")
            for cmd in command_files[:commands_copied]:
                console.print(f"  • {cmd}")

        console.print("\n[dim]Personal mode: All Quaestor files are local to this project[/dim]")
        console.print("[dim]Claude will automatically discover .claude/CLAUDE.md[/dim]")
        console.print("[dim]Commands are available from .claude/commands[/dim]")

        console.print("\n[blue]Next steps:[/blue]")
        console.print("  • Run 'quaestor configure --init' to customize command behavior")
        console.print("  • Run 'quaestor configure --command task --create-override' to override specific commands")
        console.print("\n[yellow]Remember to add .claude/ to your .gitignore![/yellow]")
    else:
        console.print("[red]No files were copied. Please check the source files exist.[/red]")
        raise typer.Exit(1)


def _init_team_mode(target_dir: Path, force: bool, contextual: bool = True):
    """Initialize in team mode (original behavior)."""
    quaestor_dir = target_dir / QUAESTOR_DIR_NAME
    manifest_path = quaestor_dir / "manifest.json"

    # Set up .claude directory in user's home
    claude_dir = DEFAULT_COMMANDS_DIR.parent
    claude_commands_dir = claude_dir / "commands"

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

    # Create .claude/commands if it doesn't exist
    claude_commands_dir.mkdir(parents=True, exist_ok=True)
    console.print(f"[green]Using .claude directory at {claude_dir}[/green]")

    # Set quaestor version in manifest
    manifest.set_quaestor_version(__version__)

    # Copy files using package resources
    copied_files = []

    # Handle CLAUDE.md smartly
    if merge_claude_md(target_dir, use_rule_engine=contextual):
        # Track in manifest as user-editable since users can modify it
        claude_path = target_dir / "CLAUDE.md"
        if claude_path.exists():
            manifest.track_file(claude_path, FileType.USER_EDITABLE, "1.0", target_dir)
            copied_files.append("CLAUDE.md")

    # Copy QUAESTOR_CLAUDE.md to .quaestor directory
    try:
        quaestor_claude_content = pkg_resources.read_text("quaestor", "QUAESTOR_CLAUDE.md")
        quaestor_claude_path = quaestor_dir / "QUAESTOR_CLAUDE.md"
        quaestor_claude_path.write_text(quaestor_claude_content)

        # Track in manifest
        version = extract_version_from_content(quaestor_claude_content) or "1.0"
        manifest.track_file(quaestor_claude_path, FileType.SYSTEM, version, target_dir)

        copied_files.append("QUAESTOR_CLAUDE.md")
        console.print("  [blue]✓[/blue] Copied QUAESTOR_CLAUDE.md")
    except Exception as e:
        console.print(f"  [yellow]⚠[/yellow] Could not copy QUAESTOR_CLAUDE.md: {e}")

    # Copy CRITICAL_RULES.md to .quaestor directory
    try:
        critical_rules_content = pkg_resources.read_text("quaestor", "CRITICAL_RULES.md")
        critical_rules_path = quaestor_dir / "CRITICAL_RULES.md"
        critical_rules_path.write_text(critical_rules_content)

        # Track in manifest
        version = extract_version_from_content(critical_rules_content) or "1.0"
        manifest.track_file(critical_rules_path, FileType.SYSTEM, version, target_dir)

        copied_files.append("CRITICAL_RULES.md")
        console.print("  [blue]✓[/blue] Copied CRITICAL_RULES.md")
    except Exception as e:
        console.print(f"  [yellow]⚠[/yellow] Could not copy CRITICAL_RULES.md: {e}")

    # Copy and convert manifest files (optional)
    console.print("[blue]Converting manifest files to AI format[/blue]")

    # ARCHITECTURE.md (optional)
    try:
        arch_path = quaestor_dir / "ARCHITECTURE.md"
        try:
            arch_content = pkg_resources.read_text("quaestor.manifest", "ARCHITECTURE.md")
            ai_arch_content = convert_manifest_to_ai_format(arch_content, "ARCHITECTURE.md")
        except Exception:
            # Try fallback to AI template
            try:
                ai_arch_content = pkg_resources.read_text("quaestor.templates", "ARCHITECTURE.template.md")
            except Exception:
                # Skip if neither source exists
                ai_arch_content = None

        if ai_arch_content:
            arch_path.write_text(ai_arch_content)

            # Track in manifest
            version = extract_version_from_content(ai_arch_content) or "1.0"
            manifest.track_file(arch_path, FileType.USER_EDITABLE, version, target_dir)

            copied_files.append("ARCHITECTURE.md")
            console.print("  [blue]✓[/blue] Copied ARCHITECTURE.md")
        else:
            console.print("  [dim]○[/dim] ARCHITECTURE.md (optional - not found)")
    except Exception:
        # Silently skip on any other errors
        pass

    # MEMORY.md (optional)
    try:
        mem_path = quaestor_dir / "MEMORY.md"
        try:
            mem_content = pkg_resources.read_text("quaestor.manifest", "MEMORY.md")
            ai_mem_content = convert_manifest_to_ai_format(mem_content, "MEMORY.md")
        except Exception:
            # Try fallback to AI template
            try:
                ai_mem_content = pkg_resources.read_text("quaestor.templates", "MEMORY.template.md")
            except Exception:
                # Skip if neither source exists
                ai_mem_content = None

        if ai_mem_content:
            mem_path.write_text(ai_mem_content)

            # Track in manifest
            version = extract_version_from_content(ai_mem_content) or "1.0"
            manifest.track_file(mem_path, FileType.USER_EDITABLE, version, target_dir)

            copied_files.append("MEMORY.md")
            console.print("  [blue]✓[/blue] Copied MEMORY.md")
        else:
            console.print("  [dim]○[/dim] MEMORY.md (optional - not found)")
    except Exception:
        # Silently skip on any other errors
        pass

    # Copy commands to ~/.claude/commands
    console.print("\n[blue]Installing command files to ~/.claude/commands:[/blue]")
    command_files = COMMAND_FILES
    commands_copied = 0

    for cmd_file in command_files:
        try:
            cmd_content = pkg_resources.read_text("quaestor.commands", cmd_file)
            (claude_commands_dir / cmd_file).write_text(cmd_content)
            console.print(f"  [blue]✓[/blue] Installed {cmd_file}")
            commands_copied += 1
        except Exception as e:
            console.print(f"  [yellow]⚠[/yellow] Could not install {cmd_file}: {e}")

    # Generate and install hooks
    console.print("\n[blue]Installing Claude hooks configuration:[/blue]")
    try:
        from .hooks import detect_project_type

        project_type = detect_project_type(target_dir)
        hooks_json_path = generate_hooks_json(target_dir, project_type)
        if hooks_json_path:
            console.print("  [blue]✓[/blue] Installed hooks in .claude/settings.json")
            console.print(f"    [dim]Location: {hooks_json_path}[/dim]")
            console.print("    [green]Hooks are now active for this project![/green]")
            copied_files.append(".claude/settings.json")
    except Exception as e:
        console.print(f"  [yellow]⚠[/yellow] Could not install hooks: {e}")

    # Save manifest
    manifest.save()

    # Generate .gitignore entries
    _update_gitignore(target_dir, mode="team")

    # Summary
    if copied_files or commands_copied > 0:
        console.print("\n[green]✅ Team mode initialization complete![/green]")

        if copied_files:
            console.print(f"\n[blue]Project files ({len(copied_files)}):[/blue]")
            for file in copied_files:
                console.print(f"  • {file}")

        if commands_copied > 0:
            console.print(f"\n[blue]Commands installed to ~/.claude/commands ({commands_copied}):[/blue]")
            for cmd in command_files[:commands_copied]:
                console.print(f"  • {cmd}")

        console.print("\n[dim]Claude will automatically discover CLAUDE.md in your project root[/dim]")
        console.print("[dim]Commands are globally available from ~/.claude/commands[/dim]")
        console.print("\n[yellow]Team mode: Commands are shared globally, project files are in .quaestor/[/yellow]")

        console.print("\n[blue]Advanced features:[/blue]")
        console.print("  • Run 'quaestor configure --init' to set project-specific command rules")
        console.print("  • Create .quaestor/commands/ for project command overrides")
    else:
        console.print("[red]No files were copied. Please check the source files exist.[/red]")
        raise typer.Exit(1)


@app.command(name="configure")
def configure(
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


@app.command(name="update")
def update(
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


# Add hooks subcommand
try:
    from .hooks import app as hooks_app

    app.add_typer(hooks_app, name="hooks", help="Claude Code hooks management")
except ImportError:
    # Hooks module not available
    pass


if __name__ == "__main__":
    app()
