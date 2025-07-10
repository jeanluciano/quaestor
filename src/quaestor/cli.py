import importlib.resources as pkg_resources
import re
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.prompt import Confirm

from .converters import convert_manifest_to_ai_format

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


def generate_hooks_json(target_dir: Path, quaestor_dir: Path, project_type: str) -> Path | None:
    """Generate hooks.json from template."""
    try:
        # Try to use Jinja2 if available
        try:
            from jinja2 import Template

            template_content = pkg_resources.read_text("quaestor.templates", "hooks.json.jinja2")
            template = Template(template_content)

            # Render template with context
            hooks_content = template.render(
                project_type=project_type,
                python_path=sys.executable,
                project_root=str(target_dir),
            )
        except ImportError:
            # Fallback to basic string replacement if Jinja2 not available
            template_content = pkg_resources.read_text("quaestor.templates", "hooks.json.jinja2")

            # Basic replacements
            hooks_content = template_content.replace("{{ project_type }}", project_type)
            hooks_content = hooks_content.replace("{{ python_path }}", sys.executable)
            hooks_content = hooks_content.replace("{{ project_root }}", str(target_dir))

            # Remove Jinja2 conditionals for simplicity in fallback
            if project_type != "python":
                # Remove Python-specific hooks
                hooks_content = re.sub(
                    r'{% if project_type == "python" %}.*?{% endif %}', "", hooks_content, flags=re.DOTALL
                )
            if project_type != "rust":
                # Remove Rust-specific hooks
                hooks_content = re.sub(
                    r'{% elif project_type == "rust" %}.*?{% endif %}', "", hooks_content, flags=re.DOTALL
                )
            if project_type != "javascript":
                # Remove JavaScript-specific hooks
                hooks_content = re.sub(
                    r'{% elif project_type == "javascript" %}.*?{% endif %}', "", hooks_content, flags=re.DOTALL
                )

        # Write hooks.json
        hooks_path = quaestor_dir / "hooks.json"
        hooks_path.write_text(hooks_content)

        return hooks_path

    except Exception as e:
        console.print(f"[yellow]Failed to generate hooks.json: {e}[/yellow]")
        return None


@app.command(name="init")
def init(
    path: Path | None = typer.Argument(None, help="Directory to initialize (default: current directory)"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing .quaestor directory"),
):
    """Initialize a .quaestor directory with context templates and install commands to ~/.claude."""
    # Determine target directory
    target_dir = path or Path.cwd()
    quaestor_dir = target_dir / ".quaestor"

    # Set up .claude directory in user's home
    claude_dir = Path.home() / ".claude"
    claude_commands_dir = claude_dir / "commands"

    # Check if .quaestor already exists
    if (
        quaestor_dir.exists()
        and not force
        and not Confirm.ask(f"[yellow].quaestor directory already exists in {target_dir}. Overwrite?[/yellow]")
    ):
        console.print("[red]Initialization cancelled.[/red]")
        raise typer.Exit()

    # Create directories
    quaestor_dir.mkdir(exist_ok=True)
    console.print(f"[green]Created .quaestor directory in {target_dir}[/green]")

    # Create .claude/commands if it doesn't exist
    claude_commands_dir.mkdir(parents=True, exist_ok=True)
    console.print(f"[green]Using .claude directory at {claude_dir}[/green]")

    # Copy files using package resources
    copied_files = []

    # Copy CLAUDE.md to project root
    try:
        claude_content = pkg_resources.read_text("quaestor", "CLAUDE.md")
        (target_dir / "CLAUDE.md").write_text(claude_content)
        copied_files.append("CLAUDE.md")
        console.print("  [blue]✓[/blue] Copied CLAUDE.md")
    except Exception as e:
        console.print(f"  [yellow]⚠[/yellow] Could not copy CLAUDE.md: {e}")

    # Copy CRITICAL_RULES.md to .quaestor directory
    try:
        critical_rules_content = pkg_resources.read_text("quaestor", "CRITICAL_RULES.md")
        (quaestor_dir / "CRITICAL_RULES.md").write_text(critical_rules_content)
        copied_files.append("CRITICAL_RULES.md")
        console.print("  [blue]✓[/blue] Copied CRITICAL_RULES.md")
    except Exception as e:
        console.print(f"  [yellow]⚠[/yellow] Could not copy CRITICAL_RULES.md: {e}")

    # Copy and convert manifest files
    console.print("[blue]Converting manifest files to AI format[/blue]")

    # ARCHITECTURE.md
    try:
        arch_content = pkg_resources.read_text("quaestor.manifest", "ARCHITECTURE.md")
        ai_arch_content = convert_manifest_to_ai_format(arch_content, "ARCHITECTURE.md")
        (quaestor_dir / "ARCHITECTURE.md").write_text(ai_arch_content)
        copied_files.append("ARCHITECTURE.md")
        console.print("  [blue]✓[/blue] Converted and copied ARCHITECTURE.md")
    except Exception:
        # Fallback to AI template if manifest not found
        try:
            ai_arch_content = pkg_resources.read_text("quaestor", "templates_ai_architecture.md")
            (quaestor_dir / "ARCHITECTURE.md").write_text(ai_arch_content)
            copied_files.append("ARCHITECTURE.md")
            console.print("  [blue]✓[/blue] Copied ARCHITECTURE.md (AI format)")
        except Exception as e2:
            console.print(f"  [yellow]⚠[/yellow] Could not copy ARCHITECTURE.md: {e2}")

    # MEMORY.md
    try:
        mem_content = pkg_resources.read_text("quaestor.manifest", "MEMORY.md")
        ai_mem_content = convert_manifest_to_ai_format(mem_content, "MEMORY.md")
        (quaestor_dir / "MEMORY.md").write_text(ai_mem_content)
        copied_files.append("MEMORY.md")
        console.print("  [blue]✓[/blue] Converted and copied MEMORY.md")
    except Exception:
        # Fallback to AI template if manifest not found
        try:
            ai_mem_content = pkg_resources.read_text("quaestor", "templates_ai_memory.md")
            (quaestor_dir / "MEMORY.md").write_text(ai_mem_content)
            copied_files.append("MEMORY.md")
            console.print("  [blue]✓[/blue] Copied MEMORY.md (AI format)")
        except Exception as e2:
            console.print(f"  [yellow]⚠[/yellow] Could not copy MEMORY.md: {e2}")

    # Copy commands to ~/.claude/commands
    console.print("\n[blue]Installing command files to ~/.claude/commands:[/blue]")
    command_files = ["project-init.md", "task-py.md", "task-rs.md", "check.md", "compose.md", "milestone-commit.md"]
    commands_copied = 0

    for cmd_file in command_files:
        try:
            cmd_content = pkg_resources.read_text("quaestor.commands", cmd_file)
            (claude_commands_dir / cmd_file).write_text(cmd_content)
            console.print(f"  [blue]✓[/blue] Installed {cmd_file}")
            commands_copied += 1
        except Exception as e:
            console.print(f"  [yellow]⚠[/yellow] Could not install {cmd_file}: {e}")

    # Generate hooks.json
    console.print("\n[blue]Generating Claude hooks configuration:[/blue]")
    try:
        from .hooks import detect_project_type

        project_type = detect_project_type(target_dir)
        hooks_json_path = generate_hooks_json(target_dir, quaestor_dir, project_type)
        if hooks_json_path:
            console.print("  [blue]✓[/blue] Generated hooks.json")
            console.print(f"    [dim]Location: {hooks_json_path}[/dim]")
            console.print(
                "    [yellow]To use: Copy to ~/.claude/settings/claude_code_hooks.json "
                "or project-specific location[/yellow]"
            )
            copied_files.append("hooks.json")
    except Exception as e:
        console.print(f"  [yellow]⚠[/yellow] Could not generate hooks.json: {e}")

    # Summary
    if copied_files or commands_copied > 0:
        console.print("\n[green]✅ Initialization complete![/green]")

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
    else:
        console.print("[red]No files were copied. Please check the source files exist.[/red]")
        raise typer.Exit(1)


# Add hooks subcommand
try:
    from .hooks import app as hooks_app

    app.add_typer(hooks_app, name="hooks", help="Claude Code hooks management")
except ImportError:
    # Hooks module not available
    pass


if __name__ == "__main__":
    app()
