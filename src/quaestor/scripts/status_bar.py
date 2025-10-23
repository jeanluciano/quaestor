#!/usr/bin/env python3
"""Claude Code status bar script for displaying active Quaestor specifications.

This script is invoked by Claude Code to display the current active specification
in the status bar. It reads from .quaestor/specs/active/ and shows the first spec
with its progress percentage.

Usage:
    Called automatically by Claude Code via .claude/settings.json configuration.
    Receives JSON context via stdin, outputs status line to stdout.

Output Format:
    🎯 spec-feature-001 (60%)
    📋 No active spec
    📋 Status unavailable (on error)
"""

import json
import sys
from pathlib import Path


def find_active_specs(workspace_dir: Path) -> list[Path]:
    """Find all active specification files in the workspace.

    Args:
        workspace_dir: Root directory of the workspace

    Returns:
        List of paths to active spec files, sorted alphabetically
    """
    active_dir = workspace_dir / ".quaestor" / "specs" / "active"

    if not active_dir.exists():
        return []

    try:
        return sorted(active_dir.glob("spec-*.md"))
    except Exception:
        return []


def parse_spec_progress(spec_path: Path) -> tuple[str, float] | None:
    """Parse a spec file to extract ID and progress percentage.

    Args:
        spec_path: Path to the specification file

    Returns:
        Tuple of (spec_id, progress_percentage) or None if parse fails
    """
    try:
        content = spec_path.read_text()

        # Extract spec ID from filename (e.g., "spec-feature-001.md" -> "spec-feature-001")
        spec_id = spec_path.stem

        # Find Acceptance Criteria section
        lines = content.split("\n")
        in_acceptance_section = False
        checked = 0
        unchecked = 0

        for line in lines:
            # Detect Acceptance Criteria section
            if line.strip().startswith("## Acceptance Criteria"):
                in_acceptance_section = True
                continue

            # Stop at next section heading
            if in_acceptance_section and line.strip().startswith("##"):
                break

            # Count checkboxes in Acceptance Criteria section
            if in_acceptance_section:
                stripped = line.strip()
                if stripped.startswith("- [x]") or stripped.startswith("- [X]"):
                    checked += 1
                elif stripped.startswith("- [ ]"):
                    unchecked += 1

        # Calculate progress
        total = checked + unchecked
        # No checkboxes found, show 0%
        progress = 0.0 if total == 0 else (checked / total) * 100.0

        return (spec_id, progress)

    except Exception:
        return None


def format_status_line(spec_id: str | None, progress: float | None) -> str:
    """Format the status bar display text.

    Args:
        spec_id: Specification ID or None if no active spec
        progress: Progress percentage or None

    Returns:
        Formatted status line string with ANSI colors
    """
    if spec_id is None:
        return "📋 No active spec"

    if progress is None:
        return f"🎯 {spec_id}"

    # Format progress as integer percentage
    progress_int = int(progress)

    # Add color coding based on progress
    if progress_int >= 80:
        # Green for near completion
        color = "\033[32m"
    elif progress_int >= 50:
        # Yellow for in progress
        color = "\033[33m"
    else:
        # Cyan for just started
        color = "\033[36m"

    reset = "\033[0m"

    return f"🎯 {spec_id} {color}({progress_int}%){reset}"


def main():
    """Main entry point for the status bar script."""
    try:
        # Read JSON context from stdin
        stdin_data = sys.stdin.read()
        context = json.loads(stdin_data) if stdin_data.strip() else {}

        # Get workspace directory from context
        workspace_path = context.get("workspace", {}).get("current")
        # Fallback to current directory if not provided
        workspace_path = Path.cwd() if not workspace_path else Path(workspace_path)

        # Find active specs
        active_specs = find_active_specs(workspace_path)

        if not active_specs:
            print(format_status_line(None, None))
            return

        # Parse first spec (sorted alphabetically)
        first_spec = active_specs[0]
        result = parse_spec_progress(first_spec)

        if result:
            spec_id, progress = result
            print(format_status_line(spec_id, progress))
        else:
            # Failed to parse, but show we found a spec
            spec_id = first_spec.stem
            print(format_status_line(spec_id, None))

    except Exception:
        # Never crash - always provide some output
        print("📋 Status unavailable")


if __name__ == "__main__":
    main()
