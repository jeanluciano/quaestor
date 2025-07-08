import importlib.resources as pkg_resources
import re
from pathlib import Path

import typer
from rich.console import Console
from rich.prompt import Confirm

app = typer.Typer(
    name="quaestor",
    help="Quaestor - Context management for AI-assisted development",
    add_completion=False,
)
console = Console()


def convert_manifest_to_ai_format(content: str, filename: str) -> str:
    """Convert human-readable manifest markdown to AI-optimized format."""
    if filename == "ARCHITECTURE.md":
        return convert_architecture_to_ai_format(content)
    elif filename == "MEMORY.md":
        return convert_memory_to_ai_format(content)
    return content


def convert_architecture_to_ai_format(content: str) -> str:
    """Convert ARCHITECTURE.md from manifest to AI format."""
    # This is a simplified conversion - in practice you'd want more sophisticated parsing
    ai_content = """<!-- META:document:architecture -->
<!-- META:version:1.0 -->
<!-- META:ai-optimized:true -->

# Project Architecture

<!-- SECTION:architecture:overview:START -->
## Architecture Overview

<!-- DATA:architecture-pattern:START -->
```yaml
pattern:
  selected: "[Choose: MVC, DDD, Microservices, Monolithic, etc.]"
  description: "Brief description of why this pattern was chosen"
```
<!-- DATA:architecture-pattern:END -->
<!-- SECTION:architecture:overview:END -->

"""

    # Extract and convert sections from the manifest content
    # This is a basic implementation - enhance as needed
    sections = re.split(r"^##\s+", content, flags=re.MULTILINE)

    for section in sections[1:]:  # Skip the first split (before any ##)
        lines = section.strip().split("\n")
        if not lines:
            continue

        section_title = lines[0].strip()

        if "layer" in section_title.lower() or "structure" in section_title.lower():
            ai_content += """
<!-- SECTION:architecture:organization:START -->
## Code Organization

<!-- DATA:directory-structure:START -->
```yaml
structure:
  - path: "src/"
    contains: []
```
<!-- DATA:directory-structure:END -->
<!-- SECTION:architecture:organization:END -->
"""
        elif "concept" in section_title.lower() or "component" in section_title.lower():
            ai_content += """
<!-- SECTION:architecture:core-concepts:START -->
## Core Concepts

<!-- DATA:key-components:START -->
```yaml
components:
  - name: "[Component Name]"
    responsibility: "[Description]"
    dependencies: []
```
<!-- DATA:key-components:END -->
<!-- SECTION:architecture:core-concepts:END -->
"""

    ai_content += (
        "\n---\n"
        "*This document describes the technical architecture of the project. "
        "Update it as architectural decisions are made or changed.*"
    )

    return ai_content


def convert_memory_to_ai_format(content: str) -> str:
    """Convert MEMORY.md from manifest to AI format."""
    ai_content = """<!-- META:document:memory -->
<!-- META:version:1.0 -->
<!-- META:ai-optimized:true -->

# Project Memory & Progress Tracking

<!-- SECTION:memory:purpose:START -->
## Document Purpose
This file tracks the current state, progress, and future plans for the project.
It serves as the "memory" of what has been done, what's in progress, and what's planned.
<!-- SECTION:memory:purpose:END -->

<!-- SECTION:memory:status:START -->
## Current Status

<!-- DATA:project-status:START -->
```yaml
status:
  last_updated: "[Date]"
  current_phase: "[Phase name]"
  current_milestone: "[Milestone name]"
  overall_progress: "[Percentage or description]"
```
<!-- DATA:project-status:END -->
<!-- SECTION:memory:status:END -->

"""

    # Extract and convert sections from the manifest content
    sections = re.split(r"^##\s+", content, flags=re.MULTILINE)

    for section in sections[1:]:  # Skip the first split
        lines = section.strip().split("\n")
        if not lines:
            continue

        section_title = lines[0].strip()

        if "timeline" in section_title.lower() or "milestone" in section_title.lower():
            ai_content += """
<!-- SECTION:memory:timeline:START -->
## Project Timeline

<!-- DATA:milestones:START -->
```yaml
milestones:
  - id: "milestone_1"
    name: "[Name]"
    status: "[Status]"
    progress: "[X]%"
    goal: "[Description]"
```
<!-- DATA:milestones:END -->
<!-- SECTION:memory:timeline:END -->
"""
        elif "action" in section_title.lower() or "next" in section_title.lower():
            ai_content += """
<!-- SECTION:memory:actions:START -->
## Next Actions

<!-- DATA:next-actions:START -->
```yaml
actions:
  immediate:
    timeframe: "This Week"
    tasks:
      - id: "immediate_1"
        task: "[High priority task]"
```
<!-- DATA:next-actions:END -->
<!-- SECTION:memory:actions:END -->
"""

    ai_content += (
        "\n---\n"
        "*This document serves as the living memory of current progress. "
        "Update it regularly as you complete tasks and learn new insights.*"
    )

    return ai_content


@app.callback()
def callback():
    """Quaestor - Context management for AI-assisted development."""
    pass


@app.command(name="init")
def init(
    path: Path | None = typer.Argument(None, help="Directory to initialize (default: current directory)"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing .quaestor directory"),
):
    """Initialize a .quaestor directory with context templates."""
    # Determine target directory
    target_dir = path or Path.cwd()
    quaestor_dir = target_dir / ".quaestor"

    # Check if .quaestor already exists
    if (
        quaestor_dir.exists()
        and not force
        and not Confirm.ask(f"[yellow].quaestor directory already exists in {target_dir}. Overwrite?[/yellow]")
    ):
        console.print("[red]Initialization cancelled.[/red]")
        raise typer.Exit()

    # Create .quaestor directory
    quaestor_dir.mkdir(exist_ok=True)
    console.print(f"[green]Created .quaestor directory in {target_dir}[/green]")

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

    # Copy commands directory
    commands_dest = quaestor_dir / "commands"
    commands_dest.mkdir(exist_ok=True)

    console.print("\n[blue]Copying command files:[/blue]")
    command_files = ["project-init.md", "task.md", "check.md", "dispatch.md"]
    for cmd_file in command_files:
        try:
            cmd_content = pkg_resources.read_text("quaestor.commands", cmd_file)
            (commands_dest / cmd_file).write_text(cmd_content)
            console.print(f"  [blue]✓[/blue] Copied {cmd_file}")
            copied_files.append(f"commands/{cmd_file}")
        except Exception as e:
            console.print(f"  [yellow]⚠[/yellow] Could not copy {cmd_file}: {e}")

    # Summary
    if copied_files:
        console.print(f"\n[green]Successfully initialized .quaestor with {len(copied_files)} template files:[/green]")
        for file in copied_files:
            console.print(f"  • {file}")
    else:
        console.print("[red]No files were copied. Please check the source files exist.[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
