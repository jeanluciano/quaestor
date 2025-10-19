"""Initialization commands for Quaestor."""

import importlib.resources as pkg_resources
import tempfile
from pathlib import Path

import typer
from rich.console import Console

from quaestor.constants import (
    QUAESTOR_CONFIG_END,
    QUAESTOR_CONFIG_START,
    QUAESTOR_DIR_NAME,
    TEMPLATE_BASE_PATH,
    TEMPLATE_FILES,
)
from quaestor.core.template_engine import get_project_data, process_template

console = Console()


def init_command(
    path: Path | None = typer.Argument(None, help="Directory to initialize (default: current directory)"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing .quaestor directory"),
    contextual: bool = typer.Option(
        True, "--contextual/--no-contextual", help="Generate contextual rules based on project analysis"
    ),
):
    """Initialize Quaestor project structure and documentation.

    Creates .quaestor directory with:
    - AGENT.md: AI development context and rules
    - ARCHITECTURE.md: System design and structure
    - RULES.md: Project-specific guidelines
    - specs/: Specification directory structure

    Also creates/updates CLAUDE.md in project root with Quaestor configuration.

    Note: Commands, agents, and hooks are provided by the Quaestor plugin.
    """
    # Determine target directory
    target_dir = path or Path.cwd()
    quaestor_dir = target_dir / QUAESTOR_DIR_NAME

    # Check if already initialized
    if quaestor_dir.exists() and not force:
        console.print("[yellow]Project already initialized. Use --force to reinitialize.[/yellow]")
        raise typer.Exit(1)

    if force and quaestor_dir.exists():
        console.print("[yellow]Force flag set - overwriting existing installation[/yellow]")

    # Create directory structure
    console.print(f"[blue]Initializing Quaestor in {target_dir}[/blue]")

    quaestor_dir.mkdir(exist_ok=True)
    (quaestor_dir / "specs" / "draft").mkdir(parents=True, exist_ok=True)
    (quaestor_dir / "specs" / "active").mkdir(parents=True, exist_ok=True)
    (quaestor_dir / "specs" / "completed").mkdir(parents=True, exist_ok=True)
    (quaestor_dir / "specs" / "archived").mkdir(parents=True, exist_ok=True)

    console.print("[green]✓ Created .quaestor directory structure[/green]")

    # Generate documentation from templates
    console.print("\n[blue]Generating documentation:[/blue]")
    project_data = get_project_data(target_dir)
    generated_files = _generate_documentation(quaestor_dir, project_data, contextual)

    # Merge/create CLAUDE.md
    _merge_claude_md(target_dir)

    # Summary
    console.print("\n[green]✅ Initialization complete![/green]")

    if generated_files:
        console.print(f"\n[blue]Generated documentation ({len(generated_files)}):[/blue]")
        for file in generated_files:
            console.print(f"  • {file}")

    console.print("\n[blue]Next steps:[/blue]")
    console.print("  • Commands available via Quaestor plugin (/plan, /impl, /research, etc.)")
    console.print("  • Use /project-init for intelligent project analysis")
    console.print("  • Use /plan to create specifications")
    console.print("  • Review and customize documentation in .quaestor/")


def _generate_documentation(quaestor_dir: Path, project_data: dict, contextual: bool = True) -> list[str]:
    """Generate documentation files from templates.

    Args:
        quaestor_dir: Path to .quaestor directory
        project_data: Project metadata for template processing
        contextual: Whether to generate contextual rules

    Returns:
        List of generated file paths (relative to project root)
    """
    generated_files = []

    for template_name, output_name in TEMPLATE_FILES.items():
        try:
            output_path = quaestor_dir / output_name

            # Read template content
            try:
                template_content = pkg_resources.read_text(TEMPLATE_BASE_PATH, template_name)
            except Exception as e:
                console.print(f"  [yellow]⚠[/yellow] Could not read template {template_name}: {e}")
                continue

            # Process template with project data
            try:
                # Create a temporary file for processing
                with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as tf:
                    tf.write(template_content)
                    temp_path = Path(tf.name)

                processed_content = process_template(temp_path, project_data)
                temp_path.unlink()  # Clean up temp file
            except Exception:
                # If processing fails, use template as-is
                processed_content = template_content

            # Write output file
            if processed_content:
                output_path.write_text(processed_content)
                generated_files.append(f".quaestor/{output_name}")
                console.print(f"  [blue]✓[/blue] Created {output_name}")

        except Exception as e:
            console.print(f"  [yellow]⚠[/yellow] Could not create {output_name}: {e}")

    return generated_files


def _merge_claude_md(target_dir: Path) -> bool:
    """Merge Quaestor include section with existing CLAUDE.md or create new one.

    Args:
        target_dir: Project root directory

    Returns:
        True if successful, False otherwise
    """
    claude_path = target_dir / "CLAUDE.md"

    try:
        # Get the include template
        try:
            include_content = pkg_resources.read_text("quaestor", "include.md")
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
