"""Main CLI application - Installation only.

This is a minimal CLI for installing Quaestor via uvx. All other functionality
is provided through the Claude Code plugin.
"""

import importlib.resources as pkg_resources
import tempfile
from pathlib import Path

import typer
from rich.console import Console

from quaestor.constants import (
    CLAUDE_DIR_NAME,
    QUAESTOR_DIR_NAME,
    SKILLS_SOURCE_DIR,
    TEMPLATE_BASE_PATH,
    TEMPLATE_FILES,
)
from quaestor.scripts.claude_md_utils import merge_claude_md
from quaestor.scripts.template_engine import get_project_data, process_template

console = Console()

# Create the main Typer application
app = typer.Typer(
    name="quaestor",
    help="Quaestor - Context management for AI-assisted development (Installation CLI)",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"], "max_content_width": 120},
)


@app.command(name="init")
def init_command(
    path: Path | None = typer.Argument(None, help="Directory to initialize (default: current directory)"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing .quaestor directory"),
):
    """Initialize Quaestor project structure and documentation.

    Creates .quaestor directory with:
    - AGENT.md: AI behavioral rules and workflow enforcement
    - ARCHITECTURE.md: System design, structure, and quality guidelines
    - specs/: Specification directory structure (draft, active, completed, archived)

    Also creates/updates CLAUDE.md in project root with Quaestor configuration.

    Note: All commands, agents, and skills are provided by the Quaestor plugin.
    This CLI is only for installation.
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
    generated_files = _generate_documentation(quaestor_dir, project_data)

    # Install project skills
    console.print("\n[blue]Installing skills:[/blue]")
    installed_skills = _install_skills(target_dir)

    # Merge/create CLAUDE.md
    result = merge_claude_md(target_dir)
    if result["success"]:
        if result["action"] == "created":
            console.print("  [blue]✓[/blue] Created CLAUDE.md with Quaestor config")
        elif result["action"] == "updated":
            console.print("  [blue]↻[/blue] Updated Quaestor config in existing CLAUDE.md")
        elif result["action"] == "prepended":
            console.print("  [blue]✓[/blue] Added Quaestor config to existing CLAUDE.md")
        elif result["action"] == "replaced":
            console.print(f"  [yellow]⚠[/yellow] {result['message']}")
    else:
        console.print(f"  [red]✗[/red] {result['message']}")

    # Summary
    console.print("\n[green]✅ Initialization complete![/green]")

    if generated_files:
        console.print(f"\n[blue]Generated documentation ({len(generated_files)}):[/blue]")
        for file in generated_files:
            console.print(f"  • {file}")

    if installed_skills:
        console.print(f"\n[blue]Installed skills ({len(installed_skills)}):[/blue]")
        for skill in installed_skills:
            console.print(f"  • {skill}")

    console.print("\n[blue]Next steps:[/blue]")
    console.print("  • All commands available via Quaestor plugin (/plan, /impl, /research, etc.)")
    console.print("  • Use /project-init for intelligent project analysis")
    console.print("  • Use /plan to create specifications")
    console.print("  • Review and customize documentation in .quaestor/")


def _generate_documentation(quaestor_dir: Path, project_data: dict) -> list[str]:
    """Generate documentation files from templates."""
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
                with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as tf:
                    tf.write(template_content)
                    temp_path = Path(tf.name)

                processed_content = process_template(temp_path, project_data)
                temp_path.unlink()
            except Exception:
                processed_content = template_content

            # Write output file
            if processed_content:
                output_path.write_text(processed_content)
                generated_files.append(f".quaestor/{output_name}")
                console.print(f"  [blue]✓[/blue] Created {output_name}")

        except Exception as e:
            console.print(f"  [yellow]⚠[/yellow] Could not create {output_name}: {e}")

    return generated_files


def _install_skills(target_dir: Path) -> list[str]:
    """Install Quaestor skills as project skills."""
    installed_skills = []
    skills_target_dir = target_dir / CLAUDE_DIR_NAME / "skills"

    try:
        skills_target_dir.mkdir(parents=True, exist_ok=True)

        try:
            from importlib.resources import files

            skills_source = files(TEMPLATE_BASE_PATH).joinpath(SKILLS_SOURCE_DIR)

            if not hasattr(skills_source, "is_dir") or not skills_source.is_dir():
                console.print("  [yellow]⚠[/yellow] Skills directory not found in package")
                return installed_skills

            for skill_dir in skills_source.iterdir():
                try:
                    if skill_dir.is_dir():
                        skill_name = skill_dir.name
                        skill_file = skill_dir / "SKILL.md"

                        if skill_file.exists():
                            target_skill_dir = skills_target_dir / skill_name
                            target_skill_dir.mkdir(exist_ok=True)

                            target_skill_file = target_skill_dir / "SKILL.md"
                            content = skill_file.read_text()
                            target_skill_file.write_text(content)

                            installed_skills.append(skill_name)
                            console.print(f"  [blue]✓[/blue] Installed {skill_name}")
                except Exception as skill_error:
                    console.print(f"  [yellow]⚠[/yellow] Could not install {skill_dir.name}: {skill_error}")

        except Exception as e:
            console.print(f"  [yellow]⚠[/yellow] Could not access skills: {e}")

    except Exception as e:
        console.print(f"  [yellow]⚠[/yellow] Could not create skills directory: {e}")

    return installed_skills


__all__ = ["app"]
