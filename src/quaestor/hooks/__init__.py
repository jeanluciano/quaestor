"""Quaestor hooks module for Claude Code integration.

This module provides automated enforcement and assistance through Claude Code hooks.
"""

import json
from pathlib import Path
from typing import Any

import typer

from ..cli import console

app = typer.Typer(name="hooks", help="Claude Code hook integration for Quaestor")


class HookResult:
    """Result of a hook execution."""

    def __init__(self, success: bool, message: str = "", data: dict[str, Any] | None = None):
        self.success = success
        self.message = message
        self.data = data or {}

    def to_json(self) -> str:
        """Convert to JSON for Claude Code."""
        return json.dumps({"success": self.success, "message": self.message, "data": self.data})

    def to_exit_code(self) -> int:
        """Convert to exit code (0 for success, 1 for failure)."""
        return 0 if self.success else 1


def get_project_root() -> Path:
    """Find the project root by looking for .quaestor directory."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".quaestor").exists():
            return current
        current = current.parent
    return Path.cwd()


def load_quaestor_config() -> dict[str, Any]:
    """Load quaestor configuration from project."""
    root = get_project_root()
    config = {}

    # Load MANIFEST.yaml if it exists
    manifest_path = root / ".quaestor" / "MANIFEST.yaml"
    if manifest_path.exists():
        try:
            import yaml

            with open(manifest_path) as f:
                config["manifest"] = yaml.safe_load(f)
        except ImportError:
            pass  # YAML not available
        except Exception:
            pass  # Invalid YAML

    # Check for project markers
    config["project_type"] = detect_project_type(root)
    config["has_critical_rules"] = (root / ".quaestor" / "CRITICAL_RULES.md").exists()
    config["has_memory"] = (root / ".quaestor" / "MEMORY.md").exists()

    return config


def detect_project_type(root: Path) -> str:
    """Detect the project type from files."""
    if (root / "pyproject.toml").exists() or (root / "requirements.txt").exists():
        return "python"
    elif (root / "Cargo.toml").exists():
        return "rust"
    elif (root / "package.json").exists():
        return "javascript"
    elif (root / "go.mod").exists():
        return "go"
    return "unknown"


def run_hook(hook_name: str, context: dict[str, Any]) -> HookResult:
    """Run a specific hook with given context."""
    # Dynamic import based on hook category
    if hook_name.startswith("enforce_"):
        from .enforcement import run_enforcement_hook

        return run_enforcement_hook(hook_name, context)
    elif hook_name.startswith("auto_"):
        from .automation import run_automation_hook

        return run_automation_hook(hook_name, context)
    elif hook_name.startswith("intel_"):
        from .intelligence import run_intelligence_hook

        return run_intelligence_hook(hook_name, context)
    else:
        return HookResult(False, f"Unknown hook: {hook_name}")


@app.command(name="enforce-research")
def enforce_research(tool: str = typer.Argument(..., help="Tool being used")):
    """Enforce Research → Plan → Implement workflow."""
    from .enforcement import check_research_before_implementation

    result = check_research_before_implementation(tool)
    print(result.message)
    raise typer.Exit(result.to_exit_code())


@app.command(name="update-memory")
def update_memory(
    from_todos: bool = typer.Option(False, "--from-todos", help="Update from TODO list"),
    milestone: str | None = typer.Option(None, "--milestone", help="Specific milestone to update"),
):
    """Update MEMORY.md with current progress."""
    from .automation import update_memory_from_todos

    if from_todos:
        result = update_memory_from_todos(milestone)
        console.print(result.message)
        raise typer.Exit(result.to_exit_code())
    else:
        console.print("[yellow]No update source specified. Use --from-todos[/yellow]")
        raise typer.Exit(1)


@app.command(name="quality-check")
def quality_check(
    block_on_fail: bool = typer.Option(False, "--block-on-fail", help="Exit with error on quality issues"),
    fix: bool = typer.Option(False, "--fix", help="Attempt to fix issues automatically"),
):
    """Run quality checks based on project type."""
    from .automation import run_quality_checks

    result = run_quality_checks(fix=fix)
    console.print(result.message)

    if block_on_fail and not result.success:
        raise typer.Exit(1)
    raise typer.Exit(0)


@app.command(name="check-milestone")
def check_milestone(
    auto_pr: bool = typer.Option(False, "--auto-pr", help="Create PR if milestone is complete"),
    milestone: str | None = typer.Option(None, "--milestone", help="Specific milestone to check"),
):
    """Check milestone completion status."""
    from .automation import check_milestone_completion

    result = check_milestone_completion(milestone, auto_pr)
    console.print(result.message)
    raise typer.Exit(result.to_exit_code())


@app.command(name="refresh-context")
def refresh_context(focus: str | None = typer.Option(None, "--focus", help="Focus area for context")):
    """Refresh and optimize Claude's context."""
    from .intelligence import refresh_claude_context

    result = refresh_claude_context(focus)
    console.print(result.message)
    raise typer.Exit(result.to_exit_code())


if __name__ == "__main__":
    app()
